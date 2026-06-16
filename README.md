# AI Knowledge & Decision Support System

An intelligent document Q&A system powered by RAG (Retrieval-Augmented Generation). Upload PDFs, text files, CSVs, or Excel spreadsheets and ask natural-language questions — answers are grounded in your documents with source citations.

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Component diagram, data flow, technology decisions |
| [Workflow](docs/WORKFLOW.md) | Step-by-step ingestion and query pipelines |
| [Limitations](docs/LIMITATIONS.md) | Known constraints and workarounds |
| [Risks](docs/RISKS.md) | Security, operational, and data risks with mitigations |

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Vector Database | Pinecone |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| LLM | HuggingFace Inference API (Llama 3.1 8B Instruct) |
| Document Parsing | PyPDF2, pandas |
| REST API (optional) | FastAPI + Uvicorn |

## Prerequisites

- Python 3.10+
- [Pinecone account](https://www.pinecone.io/) with an index created (dimension: 384, metric: cosine)
- [HuggingFace account](https://huggingface.co/) with an API token

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ambalalsonawane26/ai-knowledge-support-system.git
cd ai-knowledge-support-system

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env — set PINECONE_API_KEY, PINECONE_ENVIRONMENT, HUGGINGFACE_API_TOKEN

# 5. Run Streamlit frontend
streamlit run app/main.py

# 5b. (Optional) Run FastAPI backend in a second terminal
uvicorn backend.api:app --reload
```

## Docker (Production)

```bash
cp .env.example .env
# Fill in your API keys in .env

docker compose up --build
```

- Streamlit UI: http://localhost:8501
- FastAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Configuration

All settings are loaded from environment variables. Copy `.env.example` to `.env` and set:

| Variable | Required | Default | Description |
|---|---|---|---|
| `PINECONE_API_KEY` | Yes | — | Pinecone API key |
| `PINECONE_ENVIRONMENT` | Yes | — | Pinecone environment (e.g. `us-east-1-aws`) |
| `PINECONE_INDEX_NAME` | No | `documents` | Name of the Pinecone index |
| `HUGGINGFACE_API_TOKEN` | Yes | — | HuggingFace access token |
| `LLM_MODEL_NAME` | No | `meta-llama/Llama-3.1-8B-Instruct` | HuggingFace model ID |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `MAX_UPLOAD_SIZE_MB` | No | `50` | Max file upload size in MB |
| `CHUNK_SIZE` | No | `500` | Max characters per document chunk |
| `CHUNK_OVERLAP` | No | `50` | Overlap characters between chunks |
| `TOP_K_RETRIEVAL` | No | `5` | Number of chunks retrieved per query |
| `MAX_QUERY_LENGTH` | No | `1000` | Max characters in a user query |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:8501` | Comma-separated allowed CORS origins |

## Project Structure

```
ai-knowledge-support-system/
├── app/
│   ├── main.py                  # Streamlit UI entry point
│   ├── config.py                # Environment config loader
│   └── utils/
│       ├── document_processor.py # Parse PDF/TXT/CSV/Excel → chunks
│       ├── embeddings.py         # SentenceTransformer local embeddings
│       ├── vector_store.py       # Pinecone upsert / search / delete
│       └── llm_handler.py        # HuggingFace LLM client
├── backend/
│   ├── api.py                   # FastAPI REST API
│   ├── models.py                # Pydantic request/response models
│   └── services/
│       ├── document_service.py   # Document management
│       └── qa_service.py         # Question answering
├── docs/
│   ├── ARCHITECTURE.md
│   ├── WORKFLOW.md
│   ├── LIMITATIONS.md
│   └── RISKS.md
├── tests/                       # Pytest test suite
├── data/                        # Local file storage (gitignored)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## API Endpoints (FastAPI Backend)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + Pinecone connectivity check |
| POST | `/api/documents/upload` | Upload and index a document |
| GET | `/api/documents` | List all indexed documents |
| GET | `/api/documents/{id}` | Get document metadata |
| DELETE | `/api/documents/{id}` | Delete document and its vectors |
| POST | `/api/qa` | Ask a question, get grounded answer |
| POST | `/api/search` | Semantic search without LLM |

Full interactive docs available at http://localhost:8000/docs when the backend is running.

## Supported File Types

| Format | Notes |
|---|---|
| PDF | Text-based PDFs only; scanned PDFs require OCR |
| TXT | UTF-8 plain text |
| CSV | Rows converted to labelled text blocks |
| XLSX / XLS | Each sheet processed separately |

## Security Notes

- Never commit `.env` to version control — it is in `.gitignore`
- Set `CORS_ORIGINS` to specific domains in production (not wildcard)
- Add authentication before exposing to the public internet
- See [docs/RISKS.md](docs/RISKS.md) for a full risk assessment

## License

MIT License — see [LICENSE](LICENSE)
