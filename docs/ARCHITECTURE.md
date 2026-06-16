# Architecture — AI Knowledge & Decision Support System

## Overview

This system is a Retrieval-Augmented Generation (RAG) application that lets users upload documents and ask natural-language questions answered by an LLM grounded in the uploaded content.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface                             │
│                    Streamlit Web App (:8501)                        │
│   ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐   │
│   │  Upload Tab  │  │  Ask Questions   │  │  Manage Documents │   │
│   └──────┬───────┘  └────────┬─────────┘  └─────────┬─────────┘   │
└──────────┼───────────────────┼──────────────────────┼─────────────┘
           │                   │                        │
           ▼                   ▼                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
│                                                                      │
│  ┌───────────────────┐    ┌───────────────────┐                     │
│  │  DocumentProcessor │    │  HuggingFaceLLM   │                     │
│  │  (app/utils/)      │    │  (app/utils/)      │                     │
│  │  - PDF parsing     │    │  - Prompt builder  │                     │
│  │  - TXT/CSV/Excel   │    │  - HF Inference    │                     │
│  │  - Text chunking   │    │    API client      │                     │
│  └────────┬──────────┘    └────────┬──────────┘                     │
│           │                         │                                │
│  ┌────────▼──────────┐             │                                │
│  │  EmbeddingGenerator│             │                                │
│  │  (app/utils/)      │             │                                │
│  │  SentenceTransformer│            │                                │
│  │  (runs locally)    │             │                                │
│  └────────┬──────────┘             │                                │
└──────────┬┼──────────────────────────┼────────────────────────────┘
           ││                          │
           ▼▼                          │
┌─────────────────────┐   External     │
│  PineconeVectorStore│◄───────────────┘
│  (app/utils/)       │   (search with embedded query)
│  - upsert vectors   │
│  - semantic search  │
│  - delete vectors   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐        ┌──────────────────────────┐
│   Pinecone Cloud     │        │  HuggingFace Inference    │
│  (Vector Database)   │        │  API (Remote LLM)         │
│  - Index: documents  │        │  - Llama-3.1-8B-Instruct  │
│  - Cosine similarity │        │  (or configured model)    │
└─────────────────────┘        └──────────────────────────┘
```

## Optional REST API Layer

An optional FastAPI backend (`backend/`) mirrors all functionality via HTTP:

```
HTTP Client
    │
    ▼
FastAPI (:8000)
├── POST /api/documents/upload
├── GET  /api/documents
├── DELETE /api/documents/{id}
├── POST /api/qa
├── POST /api/search
└── GET  /health
         │
         ▼
  DocumentService / QAService
  (reuse app/utils/* under the hood)
```

## Component Responsibilities

| Component | Location | Responsibility |
|---|---|---|
| `DocumentProcessor` | `app/utils/document_processor.py` | Parse PDF/TXT/CSV/Excel → text chunks |
| `EmbeddingGenerator` | `app/utils/embeddings.py` | Convert text to 384-dim vectors locally via `sentence-transformers` |
| `PineconeVectorStore` | `app/utils/vector_store.py` | Store, query, and delete document embeddings in Pinecone |
| `HuggingFaceLLM` | `app/utils/llm_handler.py` | Build prompts and call HuggingFace Inference API |
| `DocumentService` | `backend/services/document_service.py` | Orchestrate upload → process → index pipeline |
| `QAService` | `backend/services/qa_service.py` | Orchestrate query → retrieve → generate pipeline |
| `main.py` | `app/main.py` | Streamlit UI, session state, user interactions |
| `api.py` | `backend/api.py` | FastAPI routes, request/response validation |

## Data Storage

| Data Type | Storage | Persistence |
|---|---|---|
| Uploaded files | `data/uploaded_documents/` (local disk) | Persists across restarts |
| Document vectors | Pinecone cloud index | Persistent (cloud-managed) |
| Document registry | In-memory (`DocumentService.documents`) | Lost on restart |
| Chat history | Streamlit session state | Lost on page refresh |

## Embedding Model

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Runs**: Locally in-process (no API call needed)
- **Batch processing**: 32 texts per batch

## LLM

- **Default model**: `meta-llama/Llama-3.1-8B-Instruct`
- **Interface**: HuggingFace `InferenceClient` (`chat_completion` API)
- **Max tokens**: 512 (configurable)
- **Temperature**: 0.7 (configurable)
