"""
Central configuration for the AI PDF Assistant.
Change model names, chunking, and paths here — nothing else in the
codebase should hardcode these values.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
COLLECTION_NAME = "pdf_assistant"

# ---------------------------------------------------------------------------
# Ollama models
# ---------------------------------------------------------------------------
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "gemma3:4b"

# ---------------------------------------------------------------------------
# Chunking / retrieval
# ---------------------------------------------------------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
APP_TITLE = "AI PDF Assistant"
APP_ICON = "📄"
APP_PORT = int(os.environ.get("APP_PORT", 8000))

# ---------------------------------------------------------------------------
# Server / CORS
# ---------------------------------------------------------------------------
# Comma-separated list of origins allowed to call this API, e.g. your
# deployed frontend's URL. "*" allows any origin (fine for local/dev use
# behind a tunnel, but tighten this before exposing publicly long-term).
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
