package main

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
)

// OllamaRequest represents the request structure for Ollama API
type OllamaRequest struct {
	Model    string                 `json:"model"`
	Prompt   string                 `json:"prompt"`
	Stream   bool                   `json:"stream"`
	Options  map[string]interface{} `json:"options,omitempty"`
	Template string                 `json:"template,omitempty"`
}

// OllamaResponse represents the response from Ollama API
type OllamaResponse struct {
	Model     string    `json:"model"`
	CreatedAt time.Time `json:"created_at"`
	Response  string    `json:"response"`
	Done      bool      `json:"done"`
	Context   []int     `json:"context,omitempty"`
}

// FileRequest represents the incoming request to create a file
type FileRequest struct {
	Filename     string            `json:"filename"`
	Prompt       string            `json:"prompt"`
	Context      string            `json:"context"`
	ContextFiles []string          `json:"context_files"`
	Model        string            `json:"model"`
	Options      map[string]string `json:"options"`
	SaveToFile   bool              `json:"save_to_file"` // New field
}

// FileResponse represents the response after file creation
type FileResponse struct {
	Success  bool   `json:"success"`
	Filename string `json:"filename,omitempty"`
	Content  string `json:"content,omitempty"`
	Error    string `json:"error,omitempty"`
	Duration string `json:"duration,omitempty"`
}

// PromptHistory represents a saved prompt interaction
type PromptHistory struct {
	ID           string            `json:"id"`
	Timestamp    time.Time         `json:"timestamp"`
	Model        string            `json:"model"`
	Prompt       string            `json:"prompt"`
	Context      string            `json:"context"`
	ContextFiles []string          `json:"context_files"`
	Filename     string            `json:"filename"`
	Content      string            `json:"content"`
	Duration     time.Duration     `json:"duration"`
	Options      map[string]string `json:"options,omitempty"`
}

// Config holds application configuration
type Config struct {
	OllamaURL        string
	OutputDir        string
	HistoryDir       string
	ContextDir       string
	DefaultModel     string
	MaxFileSize      int64
	MaxHistoryItems  int
	RequestTimeout   time.Duration
	AllowedFileTypes []string
}

// Server represents the HTTP server with its dependencies
type Server struct {
	config *Config
	mu     sync.RWMutex
}

var defaultConfig = &Config{
	OllamaURL:        getEnv("OLLAMA_URL", "http://localhost:11434"),
	OutputDir:        getEnv("OUTPUT_DIR", "./generated_files"),
	HistoryDir:       getEnv("HISTORY_DIR", "./prompt_history"),
	ContextDir:       getEnv("CONTEXT_DIR", "./context_files"),
	DefaultModel:     getEnv("DEFAULT_MODEL", "llama2"),
	MaxFileSize:      10 * 1024 * 1024, // 10MB
	MaxHistoryItems:  100,
	RequestTimeout:   5 * time.Minute,
	AllowedFileTypes: []string{".txt", ".md", ".js", ".py", ".go", ".json", ".xml", ".html", ".css", ".sql", ".yml", ".yaml", ".sh", ".rs", ".java", ".cpp", ".c", ".h"},
}

func main() {
	server := &Server{config: defaultConfig}

	if err := server.initializeDirectories(); err != nil {
		log.Fatalf("Failed to initialize directories: %v", err)
	}
	server.setupRoutes()
	port := getEnv("PORT", "8080")
	if !strings.HasPrefix(port, ":") {
		port = ":" + port
	}
	log.Printf("Server starting on http://localhost%s", port)
	log.Printf("Ollama URL: %s", server.config.OllamaURL)
	log.Printf("Output directory: %s", server.config.OutputDir)

	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}

func (s *Server) initializeDirectories() error {
	dirs := []string{s.config.OutputDir, s.config.HistoryDir, s.config.ContextDir}
	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("failed to create directory %s: %w", dir, err)
		}
	}
	return nil
}

func (s *Server) setupRoutes() {
	// Serve static files from the current directory
	http.Handle("/", http.FileServer(http.Dir(".")))
	// Serve generated files
	http.Handle("/generated_files/", http.StripPrefix("/generated_files/", http.FileServer(http.Dir(s.config.OutputDir))))

	http.HandleFunc("/api/create-file", s.handleCreateFile)
	http.HandleFunc("/api/models", s.handleGetModels)
	http.HandleFunc("/api/health", s.handleHealth)
	http.HandleFunc("/api/history", s.handleHistory)
	http.HandleFunc("/api/history/load", s.handleLoadHistory)
	http.HandleFunc("/api/history/delete", s.handleDeleteHistory)
	http.HandleFunc("/api/upload-context", s.handleUploadContext)
	http.HandleFunc("/api/context-files", s.handleListContextFiles)
	http.HandleFunc("/api/delete-context", s.handleDeleteContext)
	http.HandleFunc("/api/export-history", s.handleExportHistory)
}

func (s *Server) handleCreateFile(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Only POST method is supported")
		return
	}

	var req FileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if req.Prompt == "" || req.Model == "" {
		writeError(w, http.StatusBadRequest, "Prompt and model are required")
		return
	}

	if req.SaveToFile && req.Filename == "" {
		writeError(w, http.StatusBadRequest, "Filename is required when saving to file")
		return
	}

	// Read and sanitize context files
	var contextContent strings.Builder
	if len(req.ContextFiles) > 0 {
		for _, file := range req.ContextFiles {
			safePath := filepath.Clean(filepath.Join(s.config.ContextDir, file))
			if !strings.HasPrefix(safePath, s.config.ContextDir) {
				writeError(w, http.StatusBadRequest, "Invalid file path in context_files")
				return
			}
			data, err := os.ReadFile(safePath)
			if err != nil {
				writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to read context file %s: %v", file, err))
				return
			}
			contextContent.WriteString(fmt.Sprintf("\n\n### Context from file: %s\n```\n%s\n```\n", file, string(data)))
		}
	}

	fullPrompt := req.Prompt
	if req.Context != "" {
		fullPrompt = fmt.Sprintf("Context: %s\n\nTask: %s", req.Context, fullPrompt)
	}
	if contextContent.Len() > 0 {
		fullPrompt = fmt.Sprintf("%s\n\n%s", fullPrompt, contextContent.String())
	}

	ollamaReq := OllamaRequest{
		Model:   req.Model,
		Prompt:  fullPrompt,
		Stream:  true,
		Options: make(map[string]interface{}),
	}

	// Map string options to proper types
	for key, val := range req.Options {
		if floatVal, err := strconv.ParseFloat(val, 64); err == nil {
			ollamaReq.Options[key] = floatVal
		} else if intVal, err := strconv.ParseInt(val, 10, 64); err == nil {
			ollamaReq.Options[key] = intVal
		} else {
			ollamaReq.Options[key] = val
		}
	}

	log.Printf("Generating content with model %s...", req.Model)
	if req.SaveToFile {
		log.Printf("Saving to file: %s", req.Filename)
	}
	start := time.Now()

	client := &http.Client{
		Timeout: s.config.RequestTimeout,
	}

	reqBody, _ := json.Marshal(ollamaReq)
	resp, err := client.Post(s.config.OllamaURL+"/api/generate", "application/json", bytes.NewReader(reqBody))
	if err != nil {
		writeError(w, http.StatusBadGateway, fmt.Sprintf("Failed to connect to Ollama: %v", err))
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		writeError(w, resp.StatusCode, fmt.Sprintf("Ollama API returned an error: %s", string(body)))
		return
	}

	var generatedContent strings.Builder
	decoder := json.NewDecoder(resp.Body)
	for {
		var ollamaResp OllamaResponse
		if err := decoder.Decode(&ollamaResp); err != nil {
			if err == io.EOF {
				break
			}
			log.Printf("Error decoding Ollama stream: %v", err)
			break
		}
		generatedContent.WriteString(ollamaResp.Response)
		if ollamaResp.Done {
			break
		}
	}

	if generatedContent.Len() == 0 {
		writeError(w, http.StatusInternalServerError, "Ollama returned no content")
		return
	}

	duration := time.Since(start)

	var savedFilename string
	if req.SaveToFile {
		safePath := filepath.Join(s.config.OutputDir, filepath.Base(req.Filename))
		if err := os.WriteFile(safePath, []byte(generatedContent.String()), 0644); err != nil {
			writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to save file: %v", err))
			return
		}
		savedFilename = req.Filename

		// Save history only if file was saved
		history := PromptHistory{
			ID:           uuid.New().String(),
			Timestamp:    time.Now(),
			Model:        req.Model,
			Prompt:       req.Prompt,
			Context:      req.Context,
			ContextFiles: req.ContextFiles,
			Filename:     req.Filename,
			Content:      generatedContent.String(),
			Duration:     duration,
			Options:      req.Options,
		}
		historyFile, err := json.MarshalIndent(history, "", "  ")
		if err == nil {
			historyPath := filepath.Join(s.config.HistoryDir, history.ID+".json")
			if err := os.WriteFile(historyPath, historyFile, 0644); err != nil {
				log.Printf("Failed to save history file: %v", err)
			}
		}
	}

	writeJSON(w, http.StatusOK, FileResponse{
		Success:  true,
		Filename: savedFilename,
		Content:  generatedContent.String(),
		Duration: duration.String(),
	})
}

func (s *Server) handleGetModels(w http.ResponseWriter, r *http.Request) {
	resp, err := http.Get(s.config.OllamaURL + "/api/tags")
	if err != nil {
		writeError(w, http.StatusBadGateway, fmt.Sprintf("Failed to get models from Ollama: %v", err))
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to decode Ollama response: %v", err))
		return
	}

	models, ok := result["models"].([]interface{})
	if !ok {
		writeJSON(w, http.StatusOK, map[string]interface{}{"models": []interface{}{}})
		return
	}

	var cleanedModels []map[string]interface{}
	for _, m := range models {
		if model, ok := m.(map[string]interface{}); ok {
			cleanedModels = append(cleanedModels, map[string]interface{}{
				"name": model["name"],
				"size": model["size"],
			})
		}
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"models": cleanedModels})
}

func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	resp, err := http.Get(s.config.OllamaURL + "/api/tags")
	ollamaConnected := err == nil && resp.StatusCode == http.StatusOK
	if resp != nil {
		defer resp.Body.Close()
	}
	writeJSON(w, http.StatusOK, map[string]bool{"ollama_connected": ollamaConnected})
}

func (s *Server) handleHistory(w http.ResponseWriter, r *http.Request) {
	files, err := filepath.Glob(filepath.Join(s.config.HistoryDir, "*.json"))
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Failed to read history files")
		return
	}

	var history []PromptHistory
	for _, file := range files {
		data, err := os.ReadFile(file)
		if err != nil {
			log.Printf("Failed to read history file %s: %v", file, err)
			continue
		}
		var h PromptHistory
		if err := json.Unmarshal(data, &h); err != nil {
			log.Printf("Failed to unmarshal history file %s: %v", file, err)
			continue
		}
		history = append(history, h)
	}

	sort.Slice(history, func(i, j int) bool {
		return history[i].Timestamp.After(history[j].Timestamp)
	})

	writeJSON(w, http.StatusOK, map[string]interface{}{"history": history})
}

func (s *Server) handleLoadHistory(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	if id == "" {
		writeError(w, http.StatusBadRequest, "History ID is required")
		return
	}

	safePath := filepath.Clean(filepath.Join(s.config.HistoryDir, id+".json"))
	if !strings.HasPrefix(safePath, s.config.HistoryDir) {
		writeError(w, http.StatusBadRequest, "Invalid history ID")
		return
	}

	data, err := os.ReadFile(safePath)
	if err != nil {
		writeError(w, http.StatusNotFound, "History item not found")
		return
	}

	var h PromptHistory
	if err := json.Unmarshal(data, &h); err != nil {
		writeError(w, http.StatusInternalServerError, "Failed to parse history data")
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"success": true, "item": h})
}

func (s *Server) handleDeleteHistory(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		writeError(w, http.StatusMethodNotAllowed, "Only DELETE method is supported")
		return
	}

	id := r.URL.Query().Get("id")
	if id == "" {
		writeError(w, http.StatusBadRequest, "History ID is required")
		return
	}

	safePath := filepath.Clean(filepath.Join(s.config.HistoryDir, id+".json"))
	if !strings.HasPrefix(safePath, s.config.HistoryDir) {
		writeError(w, http.StatusBadRequest, "Invalid history ID")
		return
	}

	if err := os.Remove(safePath); err != nil {
		if os.IsNotExist(err) {
			writeError(w, http.StatusNotFound, "History item not found")
		} else {
			writeError(w, http.StatusInternalServerError, "Failed to delete history item")
		}
		return
	}

	writeJSON(w, http.StatusOK, map[string]bool{"success": true})
}

func (s *Server) handleUploadContext(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "Only POST method is supported")
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		writeError(w, http.StatusBadRequest, fmt.Sprintf("Failed to get file: %v", err))
		return
	}
	defer file.Close()

	if header.Size > s.config.MaxFileSize {
		writeError(w, http.StatusBadRequest, "File size exceeds the limit")
		return
	}

	ext := strings.ToLower(filepath.Ext(header.Filename))
	allowed := false
	for _, allowedExt := range s.config.AllowedFileTypes {
		if ext == allowedExt {
			allowed = true
			break
		}
	}
	if !allowed {
		writeError(w, http.StatusBadRequest, "File type is not allowed")
		return
	}

	safePath := filepath.Clean(filepath.Join(s.config.ContextDir, header.Filename))
	if !strings.HasPrefix(safePath, s.config.ContextDir) {
		writeError(w, http.StatusBadRequest, "Invalid file path")
		return
	}

	outFile, err := os.Create(safePath)
	if err != nil {
		writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to create file on server: %v", err))
		return
	}
	defer outFile.Close()

	if _, err := io.Copy(outFile, file); err != nil {
		writeError(w, http.StatusInternalServerError, fmt.Sprintf("Failed to save file: %v", err))
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"success": true, "filename": header.Filename, "size": header.Size})
}

func (s *Server) handleListContextFiles(w http.ResponseWriter, r *http.Request) {
	files, err := os.ReadDir(s.config.ContextDir)
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Failed to read context directory")
		return
	}

	var fileList []map[string]interface{}
	for _, file := range files {
		if file.IsDir() {
			continue
		}
		info, _ := file.Info()
		fileList = append(fileList, map[string]interface{}{
			"name": file.Name(),
			"size": info.Size(),
		})
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"files": fileList})
}

func (s *Server) handleDeleteContext(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		writeError(w, http.StatusMethodNotAllowed, "Only DELETE method is supported")
		return
	}
	filename := r.URL.Query().Get("filename")
	if filename == "" {
		writeError(w, http.StatusBadRequest, "Filename is required")
		return
	}

	safePath := filepath.Clean(filepath.Join(s.config.ContextDir, filename))
	if !strings.HasPrefix(safePath, s.config.ContextDir) {
		writeError(w, http.StatusBadRequest, "Invalid filename")
		return
	}

	if err := os.Remove(safePath); err != nil {
		if os.IsNotExist(err) {
			writeError(w, http.StatusNotFound, "File not found")
		} else {
			writeError(w, http.StatusInternalServerError, "Failed to delete file")
		}
		return
	}

	writeJSON(w, http.StatusOK, map[string]bool{"success": true})
}

func (s *Server) handleExportHistory(w http.ResponseWriter, r *http.Request) {
	files, err := filepath.Glob(filepath.Join(s.config.HistoryDir, "*.json"))
	if err != nil {
		writeError(w, http.StatusInternalServerError, "Failed to read history files")
		return
	}

	zipFileName := fmt.Sprintf("ollama_history_%s.zip", time.Now().Format("20060102_150405"))
	w.Header().Set("Content-Type", "application/zip")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", zipFileName))

	zipWriter := zip.NewWriter(w)
	defer zipWriter.Close()

	for _, file := range files {
		fileReader, err := os.Open(file)
		if err != nil {
			log.Printf("Failed to open history file %s: %v", file, err)
			continue
		}
		defer fileReader.Close()

		writer, err := zipWriter.Create(filepath.Base(file))
		if err != nil {
			log.Printf("Failed to create zip entry for %s: %v", file, err)
			continue
		}

		if _, err := io.Copy(writer, fileReader); err != nil {
			log.Printf("Failed to write %s to zip: %v", file, err)
			continue
		}
	}
}

// Helper function to get environment variables
func getEnv(key, fallback string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return fallback
}

// Helper function to write JSON responses
func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		log.Printf("Failed to write JSON response: %v", err)
	}
}

// Helper function to write JSON error responses
func writeError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"success": "false", "error": message})
}
