# OllaFileGene
Create local files with Ollama  

1. File Upload Interface  
  
    Drag & Drop: Drag files directly into the upload area  
    Click to Browse: Click the upload area to select files  
    Multiple Files: Upload multiple context files at once  
    File Types: Supports common formats (.txt, .md, .js, .py, .go, .json, .xml, .html, .css, .sql, .yml, .yaml)  
  
2. File Management  
  
    Visual List: See all uploaded context files with names and sizes  
    Delete Files: Remove unwanted context files with one click  
    Persistent Storage: Files are saved in ./prompt_history/context_files/ directory  
  
3. Context Integration  
  
    Automatic Inclusion: Selected files are automatically included in the prompt context  
    Smart Formatting: File contents are formatted with filename headers  
    Combined Context: Text context and file contents are merged intelligently  
  
4. Enhanced History  
  
    File Tracking: History tracks which context files were used  
    Context Indicators: Shows which files were used in historical prompts  
  
How It Works:  
  
    Upload Files:  
        Drag files to the upload area or click to browse  
        Files are instantly uploaded and shown in the list  
    Create with Context:  
        Files are automatically included as context  
        Combined with any text context you provide  
        AI receives: Text context + File contents + Your prompt  
    File Management:  
        View all uploaded files with sizes  
        Delete files you no longer need  
        Files persist between sessions  
    History Integration:  
        History shows which files were used  
        Can see context file information when loading from history  
  
Example Use Cases:  

    Code Generation: Upload example code files, documentation, or API specs  
    Documentation: Upload requirements, style guides, or reference materials  
    Data Processing: Upload sample data files or schema definitions  
    Configuration: Upload config files, templates, or environment files  
  
  


