package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// OllamaRequest represents the request structure for Ollama API
type OllamaRequest struct {
	Model  string `json:"model"`
	Prompt string `json:"prompt"`
	Stream bool   `json:"stream"`
}

// OllamaResponse represents the response from Ollama API
type OllamaResponse struct {
	Model     string    `json:"model"`
	CreatedAt time.Time `json:"created_at"`
	Response  string    `json:"response"`
	Done      bool      `json:"done"`
}

// FileRequest represents the incoming request to create a file
type FileRequest struct {
	Filename    string   `json:"filename"`
	Prompt      string   `json:"prompt"`
	Context     string   `json:"context"`
	ContextFiles []string `json:"context_files"`
	Model       string   `json:"model"`
}

// FileResponse represents the response after file creation
type FileResponse struct {
	Success  bool   `json:"success"`
	Filename string `json:"filename"`
	Content  string `json:"content"`
	Error    string `json:"error,omitempty"`
}

// PromptHistory represents a saved prompt interaction
type PromptHistory struct {
	ID           string    `json:"id"`
	Timestamp    time.Time `json:"timestamp"`
	Model        string    `json:"model"`
	Prompt       string    `json:"prompt"`
	Context      string    `json:"context"`
	ContextFiles []string  `json:"context_files"`
	Filename     string    `json:"filename"`
	Content      string    `json:"content"`
}

// Config holds application configuration
type Config struct {
	OllamaURL    string
	OutputDir    string
	HistoryDir   string
	DefaultModel string
}

var config = Config{
	OllamaURL:    "http://localhost:11434",
	OutputDir:    "./generated_files",
	HistoryDir:   "./prompt_history",
	DefaultModel: "llama2",
}

func main() {
	// Create output directories if they don't exist
	if err := os.MkdirAll(config.OutputDir, 0755); err != nil {
		log.Fatal("Failed to create output directory:", err)
	}
	if err := os.MkdirAll(config.HistoryDir, 0755); err != nil {
		log.Fatal("Failed to create history directory:", err)
	}

	// Set up routes
	http.HandleFunc("/", serveIndex)
	http.HandleFunc("/api/create-file", handleCreateFile)
	http.HandleFunc("/api/models", handleGetModels)
	http.HandleFunc("/api/health", handleHealth)
	http.HandleFunc("/api/history", handleHistory)
	http.HandleFunc("/api/history/load", handleLoadHistory)
	http.HandleFunc("/api/upload-context", handleUploadContext)
	http.HandleFunc("/api/context-files", handleListContextFiles)
	http.HandleFunc("/api/delete-context", handleDeleteContext)

	// Start server
	port := ":8080"
	log.Printf("Server starting on http://localhost%s", port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}

// serveIndex serves the HTML frontend
func serveIndex(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ollama File Creator</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .main-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .history-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-height: 600px;
            overflow-y: auto;
        }
        h1, h2 {
            color: #333;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        #context {
            min-height: 100px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        button:disabled {
            background-color: #ccc;
            cursor: not-allowed;
        }
        button.secondary {
            background-color: #6c757d;
        }
        button.secondary:hover {
            background-color: #5a6268;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }
        .result h3 {
            margin-top: 0;
            color: #333;
        }
        .result pre {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .error {
            color: #dc3545;
            padding: 10px;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            margin-top: 10px;
        }
        .success {
            color: #155724;
            padding: 10px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            margin-top: 10px;
        }
        .loading {
            display: none;
            color: #666;
            margin-top: 10px;
        }
        .status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status.online {
            background-color: #28a745;
        }
        .status.offline {
            background-color: #dc3545;
        }
        .history-item {
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .history-item:hover {
            background-color: #f8f9fa;
        }
        .history-meta {
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 10px;
        }
        .history-filename {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .history-prompt {
            color: #555;
            font-size: 14px;
            max-height: 60px;
            overflow: hidden;
        }
        .context-files {
            margin-bottom: 20px;
        }
        .file-upload {
            border: 2px dashed #ddd;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: border-color 0.2s;
            margin-bottom: 15px;
        }
        .file-upload:hover {
            border-color: #007bff;
        }
        .file-upload.dragover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        .uploaded-files {
            margin-top: 15px;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            margin-bottom: 5px;
        }
        .file-item .file-name {
            font-weight: 500;
            color: #333;
        }
        .file-item .file-size {
            font-size: 12px;
            color: #666;
        }
        .file-item .delete-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        .file-item .delete-btn:hover {
            background: #c82333;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .main-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ollama File Creator</h1>
        <div id="status">
            <p><span class="status offline" id="statusDot"></span> <span id="statusText">Checking connection...</span></p>
        </div>
    </div>
    
    <div class="main-container">
        <div class="form-container">
            <form id="fileForm">
                <div class="form-group">
                    <label for="model">Model:</label>
                    <select id="model" name="model" required>
                        <option value="">Loading models...</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="filename">Filename:</label>
                    <input type="text" id="filename" name="filename" placeholder="example.txt" required>
                </div>
                
                <div class="form-group">
                    <label for="context">Text Context (optional):</label>
                    <textarea id="context" name="context" placeholder="Provide additional context, requirements, or examples to help generate better results..."></textarea>
                </div>
                
                <div class="form-group context-files">
                    <label>Context Files (optional):</label>
                    <div class="file-upload" id="fileUpload">
                        <p>Click or drag files here to add context</p>
                        <input type="file" id="fileInput" multiple style="display: none;" accept=".txt,.md,.js,.py,.go,.json,.xml,.html,.css,.sql,.yml,.yaml">
                    </div>
                    <div class="uploaded-files" id="uploadedFiles"></div>
                </div>
                
                <div class="form-group">
                    <label for="prompt">Prompt:</label>
                    <textarea id="prompt" name="prompt" placeholder="Create a Python script that..." required></textarea>
                </div>
                
                <div class="button-group">
                    <button type="submit" id="submitBtn">Create File</button>
                    <button type="button" id="clearBtn" class="secondary">Clear Form</button>
                </div>
                <div class="loading" id="loading">Creating file... This may take a moment.</div>
            </form>
            
            <div id="result"></div>
        </div>
        
        <div class="history-container">
            <h2>Prompt History</h2>
            <div id="historyList">
                <p>Loading history...</p>
            </div>
        </div>
    </div>

    <script>
        let historyData = [];
        let contextFiles = [];

        // File upload handling
        const fileUpload = document.getElementById('fileUpload');
        const fileInput = document.getElementById('fileInput');
        const uploadedFilesDiv = document.getElementById('uploadedFiles');

        fileUpload.addEventListener('click', () => fileInput.click());
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });
        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('dragover');
        });
        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        async function handleFiles(files) {
            for (let file of files) {
                await uploadContextFile(file);
            }
            loadContextFiles();
        }

        async function uploadContextFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/upload-context', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                console.error('Failed to upload file:', error);
                alert('Failed to upload file: ' + file.name);
            }
        }

        async function loadContextFiles() {
            try {
                const response = await fetch('/api/context-files');
                const data = await response.json();
                contextFiles = data.files || [];
                renderContextFiles();
            } catch (error) {
                console.error('Failed to load context files:', error);
            }
        }

        function renderContextFiles() {
            if (contextFiles.length === 0) {
                uploadedFilesDiv.innerHTML = '';
                return;
            }

            const filesHTML = contextFiles.map(file => 
                '<div class="file-item">' +
                    '<div>' +
                        '<span class="file-name">' + file.name + '</span>' +
                        '<span class="file-size"> (' + formatFileSize(file.size) + ')</span>' +
                    '</div>' +
                    '<button class="delete-btn" onclick="deleteContextFile(\'' + file.name + '\')">Delete</button>' +
                '</div>'
            ).join('');

            uploadedFilesDiv.innerHTML = filesHTML;
        }

        async function deleteContextFile(filename) {
            try {
                const response = await fetch('/api/delete-context?filename=' + encodeURIComponent(filename), {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadContextFiles();
                }
            } catch (error) {
                console.error('Failed to delete file:', error);
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // Check server health
        async function checkHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                
                if (data.ollama_connected) {
                    statusDot.className = 'status online';
                    statusText.textContent = 'Connected to Ollama';
                } else {
                    statusDot.className = 'status offline';
                    statusText.textContent = 'Ollama not connected - please ensure Ollama is running';
                }
            } catch (error) {
                console.error('Health check failed:', error);
            }
        }

        // Load available models
        async function loadModels() {
            try {
                const response = await fetch('/api/models');
                const data = await response.json();
                const select = document.getElementById('model');
                
                select.innerHTML = '';
                
                if (data.models && data.models.length > 0) {
                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.name;
                        if (model.name === 'llama2') {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    });
                } else {
                    select.innerHTML = '<option value="">No models available</option>';
                }
            } catch (error) {
                console.error('Failed to load models:', error);
                document.getElementById('model').innerHTML = '<option value="">Failed to load models</option>';
            }
        }

        // Load prompt history
        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                historyData = data.history || [];
                renderHistory();
            } catch (error) {
                console.error('Failed to load history:', error);
                document.getElementById('historyList').innerHTML = '<p>Failed to load history</p>';
            }
        }

        // Render history list
        function renderHistory() {
            const historyList = document.getElementById('historyList');
            
            if (historyData.length === 0) {
                historyList.innerHTML = '<p>No history yet. Create your first file!</p>';
                return;
            }

            const historyHTML = historyData
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
                .map(item => {
                    const date = new Date(item.timestamp).toLocaleDateString();
                    const time = new Date(item.timestamp).toLocaleTimeString();
                    const truncatedPrompt = item.prompt.length > 100 ? 
                        item.prompt.substring(0, 100) + '...' : item.prompt;
                    
                    return '<div class="history-item" onclick="loadHistoryItem(\'' + item.id + '\')">' +
                        '<div class="history-meta">' + date + ' ' + time + ' - ' + item.model + '</div>' +
                        '<div class="history-filename">' + item.filename + '</div>' +
                        '<div class="history-prompt">' + truncatedPrompt + '</div>' +
                        '</div>';
                }).join('');

            historyList.innerHTML = historyHTML;
        }

        // Load a specific history item
        async function loadHistoryItem(id) {
            try {
                const response = await fetch('/api/history/load?id=' + id);
                const data = await response.json();
                
                if (data.success) {
                    const item = data.item;
                    document.getElementById('model').value = item.model;
                    document.getElementById('filename').value = item.filename;
                    document.getElementById('context').value = item.context || '';
                    document.getElementById('prompt').value = item.prompt;
                    
                    // Load context files if any
                    if (item.context_files && item.context_files.length > 0) {
                        // Show info about context files from history
                        const contextInfo = '<div style="margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 5px; font-size: 14px;">' +
                            '<strong>Note:</strong> This prompt used context files: ' + item.context_files.join(', ') +
                            '</div>';
                        document.getElementById('result').innerHTML = contextInfo;
                    }
                    
                    // Show the previous result
                    const resultDiv = document.getElementById('result');
                    const existingContent = resultDiv.innerHTML;
                    resultDiv.innerHTML = existingContent + '<div class="success">Loaded from history</div>' +
                        '<div class="result">' +
                        '<h3>Previous Result: ' + item.filename + '</h3>' +
                        '<pre>' + escapeHtml(item.content) + '</pre>' +
                        '</div>';
                }
            } catch (error) {
                console.error('Failed to load history item:', error);
            }
        }

        // Clear form
        function clearForm() {
            document.getElementById('filename').value = '';
            document.getElementById('context').value = '';
            document.getElementById('prompt').value = '';
            document.getElementById('result').innerHTML = '';
        }

        // Handle form submission
        document.getElementById('fileForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            const formData = {
                filename: document.getElementById('filename').value,
                prompt: document.getElementById('prompt').value,
                context: document.getElementById('context').value,
                context_files: contextFiles.map(f => f.name),
                model: document.getElementById('model').value
            };
            
            try {
                const response = await fetch('/api/create-file', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = '<div class="success">File created successfully!</div>' +
                        '<div class="result">' +
                        '<h3>File: ' + data.filename + '</h3>' +
                        '<pre>' + escapeHtml(data.content) + '</pre>' +
                        '</div>';
                    
                    // Reload history to show the new entry
                    loadHistory();
                } else {
                    resultDiv.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        // Clear form button
        document.getElementById('clearBtn').addEventListener('click', clearForm);
        
        // HTML escape function
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Initialize
        checkHealth();
        loadModels();
        loadHistory();
        loadContextFiles();
        setInterval(checkHealth, 5000); // Check health every 5 seconds
    </script>
</body>
</html>`
	
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprint(w, html)
}

// handleCreateFile handles file creation requests
func handleCreateFile(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req FileRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		sendJSON(w, FileResponse{Success: false, Error: "Invalid request"}, http.StatusBadRequest)
		return
	}

	// Validate filename
	if req.Filename == "" {
		sendJSON(w, FileResponse{Success: false, Error: "Filename is required"}, http.StatusBadRequest)
		return
	}

	// Clean filename
	req.Filename = filepath.Base(req.Filename)
	
	// Use default model if not specified
	if req.Model == "" {
		req.Model = config.DefaultModel
	}

	// Build prompt with context if provided
	fullPrompt := req.Prompt
	contextParts := []string{}
	
	if req.Context != "" {
		contextParts = append(contextParts, req.Context)
	}
	
	// Add file contents as context
	for _, filename := range req.ContextFiles {
		content, err := readContextFile(filename)
		if err != nil {
			log.Printf("Failed to read context file %s: %v", filename, err)
			continue
		}
		contextParts = append(contextParts, fmt.Sprintf("File: %s\n%s", filename, content))
	}
	
	if len(contextParts) > 0 {
		fullPrompt = fmt.Sprintf("Context:\n%s\n\nTask: %s", strings.Join(contextParts, "\n\n---\n\n"), req.Prompt)
	}

	// Call Ollama API
	content, err := generateContent(req.Model, fullPrompt)
	if err != nil {
		sendJSON(w, FileResponse{Success: false, Error: fmt.Sprintf("Ollama error: %v", err)}, http.StatusInternalServerError)
		return
	}

	// Create file
	filePath := filepath.Join(config.OutputDir, req.Filename)
	if err := os.WriteFile(filePath, []byte(content), 0644); err != nil {
		sendJSON(w, FileResponse{Success: false, Error: fmt.Sprintf("Failed to create file: %v", err)}, http.StatusInternalServerError)
		return
	}

	// Save to history
	historyItem := PromptHistory{
		ID:           generateID(),
		Timestamp:    time.Now(),
		Model:        req.Model,
		Prompt:       req.Prompt,
		Context:      req.Context,
		ContextFiles: req.ContextFiles,
		Filename:     req.Filename,
		Content:      content,
	}
	saveHistoryItem(historyItem)

	sendJSON(w, FileResponse{
		Success:  true,
		Filename: req.Filename,
		Content:  content,
	}, http.StatusOK)
}

// generateContent calls Ollama API to generate content
func generateContent(model, prompt string) (string, error) {
	ollamaReq := OllamaRequest{
		Model:  model,
		Prompt: prompt,
		Stream: false,
	}

	jsonData, err := json.Marshal(ollamaReq)
	if err != nil {
		return "", err
	}

	resp, err := http.Post(config.OllamaURL+"/api/generate", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("failed to connect to Ollama: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("Ollama returned status %d: %s", resp.StatusCode, string(body))
	}

	var ollamaResp OllamaResponse
	if err := json.NewDecoder(resp.Body).Decode(&ollamaResp); err != nil {
		return "", err
	}

	return strings.TrimSpace(ollamaResp.Response), nil
}

// handleGetModels returns available Ollama models
func handleGetModels(w http.ResponseWriter, r *http.Request) {
	resp, err := http.Get(config.OllamaURL + "/api/tags")
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to connect to Ollama"}, http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to parse response"}, http.StatusInternalServerError)
		return
	}

	sendJSON(w, result, http.StatusOK)
}

// handleHealth checks if Ollama is accessible
func handleHealth(w http.ResponseWriter, r *http.Request) {
	ollamaConnected := false
	
	// Try to connect to Ollama
	resp, err := http.Get(config.OllamaURL + "/api/tags")
	if err == nil {
		resp.Body.Close()
		if resp.StatusCode == http.StatusOK {
			ollamaConnected = true
		}
	}

	sendJSON(w, map[string]bool{
		"server_running":   true,
		"ollama_connected": ollamaConnected,
	}, http.StatusOK)
}

// handleHistory returns the prompt history
func handleHistory(w http.ResponseWriter, r *http.Request) {
	history, err := loadHistory()
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to load history"}, http.StatusInternalServerError)
		return
	}

	sendJSON(w, map[string]interface{}{"history": history}, http.StatusOK)
}

// handleLoadHistory loads a specific history item
func handleLoadHistory(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	if id == "" {
		sendJSON(w, map[string]interface{}{"success": false, "error": "ID is required"}, http.StatusBadRequest)
		return
	}

	history, err := loadHistory()
	if err != nil {
		sendJSON(w, map[string]interface{}{"success": false, "error": "Failed to load history"}, http.StatusInternalServerError)
		return
	}

	for _, item := range history {
		if item.ID == id {
			sendJSON(w, map[string]interface{}{"success": true, "item": item}, http.StatusOK)
			return
		}
	}

	sendJSON(w, map[string]interface{}{"success": false, "error": "History item not found"}, http.StatusNotFound)
}

// handleUploadContext handles context file uploads
func handleUploadContext(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Parse multipart form
	err := r.ParseMultipartForm(10 << 20) // 10MB max
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to parse form"}, http.StatusBadRequest)
		return
	}

	file, header, err := r.FormFile("file")
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to get file"}, http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Clean filename and create context directory
	contextDir := filepath.Join(config.HistoryDir, "context_files")
	if err := os.MkdirAll(contextDir, 0755); err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to create context directory"}, http.StatusInternalServerError)
		return
	}

	filename := filepath.Base(header.Filename)
	filePath := filepath.Join(contextDir, filename)

	// Create the file
	dst, err := os.Create(filePath)
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to create file"}, http.StatusInternalServerError)
		return
	}
	defer dst.Close()

	// Copy file contents
	_, err = io.Copy(dst, file)
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to save file"}, http.StatusInternalServerError)
		return
	}

	sendJSON(w, map[string]interface{}{"success": true, "filename": filename}, http.StatusOK)
}

// handleListContextFiles returns list of uploaded context files
func handleListContextFiles(w http.ResponseWriter, r *http.Request) {
	contextDir := filepath.Join(config.HistoryDir, "context_files")
	
	files, err := os.ReadDir(contextDir)
	if err != nil {
		// Directory doesn't exist yet, return empty list
		sendJSON(w, map[string]interface{}{"files": []interface{}{}}, http.StatusOK)
		return
	}

	var fileList []map[string]interface{}
	for _, file := range files {
		if file.IsDir() {
			continue
		}
		
		info, err := file.Info()
		if err != nil {
			continue
		}
		
		fileList = append(fileList, map[string]interface{}{
			"name": file.Name(),
			"size": info.Size(),
		})
	}

	sendJSON(w, map[string]interface{}{"files": fileList}, http.StatusOK)
}

// handleDeleteContext deletes a context file
func handleDeleteContext(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	filename := r.URL.Query().Get("filename")
	if filename == "" {
		sendJSON(w, map[string]interface{}{"error": "Filename is required"}, http.StatusBadRequest)
		return
	}

	// Clean filename for security
	filename = filepath.Base(filename)
	contextDir := filepath.Join(config.HistoryDir, "context_files")
	filePath := filepath.Join(contextDir, filename)

	err := os.Remove(filePath)
	if err != nil {
		sendJSON(w, map[string]interface{}{"error": "Failed to delete file"}, http.StatusInternalServerError)
		return
	}

	sendJSON(w, map[string]interface{}{"success": true}, http.StatusOK)
}

// readContextFile reads a context file and returns its content
func readContextFile(filename string) (string, error) {
	contextDir := filepath.Join(config.HistoryDir, "context_files")
	filePath := filepath.Join(contextDir, filename)
	
	content, err := os.ReadFile(filePath)
	if err != nil {
		return "", err
	}
	
	return string(content), nil
}
func saveHistoryItem(item PromptHistory) error {
	filename := filepath.Join(config.HistoryDir, fmt.Sprintf("%s.json", item.ID))
	data, err := json.MarshalIndent(item, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filename, data, 0644)
}

// loadHistory loads all history items
func loadHistory() ([]PromptHistory, error) {
	var history []PromptHistory

	files, err := os.ReadDir(config.HistoryDir)
	if err != nil {
		return history, err
	}

	for _, file := range files {
		if !strings.HasSuffix(file.Name(), ".json") {
			continue
		}

		filePath := filepath.Join(config.HistoryDir, file.Name())
		data, err := os.ReadFile(filePath)
		if err != nil {
			continue
		}

		var item PromptHistory
		if err := json.Unmarshal(data, &item); err != nil {
			continue
		}

		history = append(history, item)
	}

	return history, nil
}

// generateID generates a simple ID for history items
func generateID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}

// sendJSON sends JSON response
func sendJSON(w http.ResponseWriter, data interface{}, status int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}
