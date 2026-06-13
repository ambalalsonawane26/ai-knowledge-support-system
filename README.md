# AI Knowledge and Decision Support System

An intelligent document-based Q&A system that leverages AI to provide grounded, contextual answers from your uploaded documents.

## Features

- **Multi-Format Document Support**: Upload PDFs, TXT, CSV, and Excel files
- **Vector-Based Retrieval**: Fast semantic search using Pinecone vector database
- **LLM-Powered Responses**: Generate accurate, grounded answers using Hugging Face models
- **Streamlit Interface**: User-friendly web interface for interaction
- **Document Management**: Upload, process, and manage multiple documents
- **Conversation History**: Track and review Q&A interactions

## Tech Stack

- **Frontend**: Streamlit
- **Vector Database**: Pinecone
- **LLM**: Hugging Face Transformers
- **Document Processing**: LangChain, PyPDF2, pandas
- **Backend**: Python 3.8+

## Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/ambalalsonawane26/ai-knowledge-support-system.git
cd ai-knowledge-support-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run the application**
```bash
streamlit run app/main.py
```

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup and installation guide
- **[README.md](README.md)** - Full project documentation

## Project Structure

```
├── app/                    # Streamlit application
│   ├── main.py            # Entry point
│   ├── config.py          # Configuration
│   └── utils/             # Utility modules
├── backend/               # FastAPI backend (optional)
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
└── .env.example          # Environment template
```

## API Endpoints (Optional Backend)

- `POST /api/documents/upload` - Upload a document
- `GET /api/documents` - List documents
- `POST /api/qa` - Ask a question
- `GET /api/search` - Search documents

## Features

### Document Processing
- Automatic chunking with overlap
- Support for multiple file formats
- Metadata extraction

### Semantic Search
- Vector-based similarity search
- Top-K retrieval
- Metadata filtering

### Answer Generation
- Context-aware responses
- Source citations
- Conversation history

## Configuration

Edit `.env` file with your settings:

```
PINCONE_API_KEY=your_key
PINCONE_ENVIRONMENT=your_environment
PINCONE_INDEX_NAME=documents
HUGGINGFACE_API_TOKEN=your_token
LLM_MODEL_NAME=mistral-7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## License

MIT License - see LICENSE file for details