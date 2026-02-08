import os

WORKSPACE = "workspace"
ARCHIVE_DIR = os.path.join(WORKSPACE, ".archive")
LOG_DIR = os.path.join(WORKSPACE, "logs")
SESSION_FILE = "session_metadata.json"

REQUIRED_LIBS = ["psutil", "cpuinfo", "black", "pylint", "bandit"]

DANGEROUS_TOKENS = [
    "os.system",
    "subprocess",
    "rm -rf",
    "shutil.rmtree",
]

OLLAMA_DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
