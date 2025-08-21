# Ollama File Creator

The **Ollama File Creator** is a simple yet powerful web application built with Go (backend) and HTML/JavaScript/CSS (frontend). It lets you interact with a locally running [Ollama](https://ollama.com/) large language model (LLM) to generate code or text files directly from your browser. You can provide prompts, additional context, and even upload context files to guide the LLM's output. The application also keeps a history of your generations for easy access and reuse.

---

## ✨ Features

* **Generate Files with LLMs**: Use your local Ollama models to create code, scripts, documentation, or any text-based content.
* **Flexible Prompting**: Provide detailed prompts and additional context to steer the LLM's generation.
* **Context File Support**: Upload relevant files (e.g., existing code, documentation snippets) to serve as extra context for the LLM.
* **Optional File Saving**: Choose whether to save the generated content to a file on your server or just display it in the browser.
* **Generation History**: View a chronological list of your past file creations, including the prompt, model used, and generated content.
* **Export History**: Download all your prompt history as a ZIP archive.
* **Ollama Health Check**: A real-time indicator shows the connection status to your Ollama server.
* **Model Management**: Automatically lists available Ollama models, allowing you to select your preferred one.
* **User-Friendly Interface**: A responsive and intuitive web interface for easy interaction.

---

## 🚀 Getting Started

To get this application up and running, you'll need a few prerequisites and then follow the installation steps.

### Prerequisites

* **Go (Golang)**: Make sure you have Go installed (version 1.18 or higher is recommended). You can download it from [golang.org](https://golang.org/dl/).
* **Ollama**: This application relies on a running Ollama instance with at least one model downloaded.
    * Download and install Ollama from [ollama.com](https://ollama.com/).
    * Pull a model, for example, Llama 2: `ollama pull llama2`

### Installation

1.  **Clone the Repository (or create files manually)**:
    If you're starting from scratch, create a directory for your project and add the `OllaFileGene2.go` and `index.html` files into it.

2.  **Initialize Go Module**:
    Open your terminal, navigate to the project directory (where `OllaFileGene2.go` is located), and run:
    ```bash
    go mod init ollama-file-creator
    ```
    (You can replace `ollama-file-creator` with any name you like, but this is a good, descriptive default.)

3.  **Download Dependencies**:
    Fetch the necessary Go packages (like `github.com/google/uuid`):
    ```bash
    go mod tidy
    ```

---

## 🏃 Running the Application

Once you've completed the installation, you can run the application:

```bash
go run OllaFileGene2.go


Ollama File Creator

The Ollama File Creator is a simple yet powerful web application built with Go (backend) and HTML/JavaScript/CSS (frontend). It lets you interact with a locally running Ollama large language model (LLM) to generate code or text files directly from your browser. You can provide prompts, additional context, and even upload context files to guide the LLM's output. The application also keeps a history of your generations for easy access and reuse.
✨ Features

    Generate Files with LLMs: Use your local Ollama models to create code, scripts, documentation, or any text-based content.

    Flexible Prompting: Provide detailed prompts and additional context to steer the LLM's generation.

    Context File Support: Upload relevant files (e.g., existing code, documentation snippets) to serve as extra context for the LLM.

    Optional File Saving: Choose whether to save the generated content to a file on your server or just display it in the browser.

    Generation History: View a chronological list of your past file creations, including the prompt, model used, and generated content.

    Export History: Download all your prompt history as a ZIP archive.

    Ollama Health Check: A real-time indicator shows the connection status to your Ollama server.

    Model Management: Automatically lists available Ollama models, allowing you to select your preferred one.

    User-Friendly Interface: A responsive and intuitive web interface for easy interaction.

🚀 Getting Started

To get this application up and running, you'll need a few prerequisites and then follow the installation steps.
Prerequisites

    Go (Golang): Make sure you have Go installed (version 1.18 or higher is recommended). You can download it from golang.org.

    Ollama: This application relies on a running Ollama instance with at least one model downloaded.

        Download and install Ollama from ollama.com.

        Pull a model, for example, Llama 2: ollama pull llama2

Installation

    Clone the Repository (or create files manually):
    If you're starting from scratch, create a directory for your project and add the OllaFileGene2.go and index.html files into it.

    Initialize Go Module:
    Open your terminal, navigate to the project directory (where OllaFileGene2.go is located), and run:

    go mod init ollama-file-creator

    (You can replace ollama-file-creator with any name you like, but this is a good, descriptive default.)

    Download Dependencies:
    Fetch the necessary Go packages (like github.com/google/uuid):

    go mod tidy

🏃 Running the Application

Once you've completed the installation, you can run the application:

go run OllaFileGene2.go

The server will start on http://localhost:8080 by default. You'll see output in your terminal indicating the server is running.

Open your web browser and navigate to http://localhost:8080.
💡 Usage
Create New File

    Model Selection: Choose an available LLM from the "Model" dropdown.

    Filename: Enter the desired name for your output file (e.g., my_script.py, report.md). This is required if "Save to file" is checked.

    Save to file (checkbox): Check this box if you want the generated content to be saved as a file in the generated_files directory and recorded in the history. Uncheck it to just display the content in the browser.

    Additional Context (optional): Provide any extra instructions, constraints, or background information for the LLM.

    Context Files (optional): Drag and drop files or click the upload zone to include their content as part of the LLM's context.

    Prompt: Enter your main instruction for what you want the LLM to generate.

    Click the "✨ Create File" button.

The generated content will appear in the "Result" section below the form. If "Save to file" was checked, you'll also see a link to download the file.
Prompt History

The right-hand panel displays a history of your generated files.

    Click on any history item to automatically populate the "Create New File" form with the details of that past generation.

    The "📦 Export All" button allows you to download a ZIP archive containing all your stored prompt history (JSON files).

📂 Project Structure

.
├── OllaFileGene2.go     # Go backend server logic
├── index.html           # Frontend HTML, CSS, and JavaScript
├── go.mod               # Go module definition
├── go.sum               # Go module checksums
├── generated_files/     # Directory for generated output files (created automatically)
├── prompt_history/      # Directory for storing prompt history (JSON files, created automatically)
└── context_files/       # Directory for uploaded context files (created automatically)

⚙️ Configuration

You can configure the application using environment variables:

    PORT: The port on which the server will listen (default: 8080).

    OLLAMA_URL: The URL of your Ollama instance (default: http://localhost:11434).

    OUTPUT_DIR: Directory to save generated files (default: ./generated_files).

    HISTORY_DIR: Directory to save prompt history JSON files (default: ./prompt_history).

    CONTEXT_DIR: Directory to save uploaded context files (default: ./context_files).

    DEFAULT_MODEL: The default Ollama model to pre-select in the dropdown (default: llama2).

Example (.env file setup or command line):

# In your terminal before running 'go run OllaFileGene2.go'
export PORT=9000
export OLLAMA_URL=http://my-ollama-host:11434
export DEFAULT_MODEL=mistral

# Or create a .env file and use a tool like 'github.com/joho/godotenv'
# to load them if you expand the Go code to do so.

🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to contribute.

    Fork the repository.

    Create your feature branch (git checkout -b feature/AmazingFeature).

    Commit your changes (git commit -m 'Add some AmazingFeature').

    Push to the branch (git push origin feature/AmazingFeature).

    Open a Pull Request.

