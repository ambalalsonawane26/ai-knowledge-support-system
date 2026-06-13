"""
Configuration settings for the AI Knowledge Support System
Loads from environment variables or uses defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Pinecone Configuration
PINCONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINCONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINCONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "documents")

# Hugging Face Configuration
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistral-7b")

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))

# Directory Configuration
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, os.getenv("UPLOAD_FOLDER", "data/uploaded_documents"))
PROCESSED_FOLDER = os.path.join(PROJECT_ROOT, os.getenv("PROCESSED_FOLDER", "data/processed"))

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Supported file types
SUPPORTED_FILE_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel"
}

# API Configuration (Optional Backend)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "['http://localhost:3000', 'http://localhost:8501']")

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_config": {
        "page_title": "AI Knowledge Support System",
        "page_icon": "🤖",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
    }
}

class ConfigError(Exception):
    """Configuration error exception"""
    pass


def validate_config():
    """Validate that all required configuration is present"""
    if not PINECONE_API_KEY:
        raise ConfigError("PINECONE_API_KEY environment variable is not set")
    if not PINECONE_ENVIRONMENT:
        raise ConfigError("PINECONE_ENVIRONMENT environment variable is not set")
    if not HUGGINGFACE_API_TOKEN:
        raise ConfigError("HUGGINGFACE_API_TOKEN environment variable is not set")
    
    return True