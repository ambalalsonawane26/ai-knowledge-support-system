# Workflow — AI Knowledge & Decision Support System

## 1. Document Ingestion Pipeline

```
User selects file(s) in UI
        │
        ▼
File size validation (≤ MAX_UPLOAD_SIZE_MB, default 100 MB)
        │
        ▼
File saved to disk
  data/uploaded_documents/<filename>
        │
        ▼
DocumentProcessor.process_file()
  ├── PDF  → PyPDF2: extract text page-by-page → concatenate
  ├── TXT  → read with UTF-8 encoding
  ├── CSV  → pandas: convert rows to labelled text block
  └── XLSX → pandas: per-sheet text block
        │
        ▼
_chunk_text()
  Split text on double-newline (paragraphs)
  Build chunks up to CHUNK_SIZE characters (default 500)
  Oversized paragraphs split further with CHUNK_OVERLAP (default 50)
        │
        ▼
EmbeddingGenerator.generate_embeddings_batch()
  SentenceTransformer encodes all chunks locally
  Output: List[List[float]] — 384-dim vectors
        │
        ▼
PineconeVectorStore.upsert_documents()
  Each chunk → vector record:
    id:       "<doc_id>_chunk_<idx>"
    values:   384-float embedding
    metadata: { document_id, chunk_index, text, file_name, file_type, ... }
  Batch upserted to Pinecone index
        │
        ▼
Session state updated (indexed_documents list)
Success message shown to user
```

## 2. Question Answering (RAG) Pipeline

```
User types question in chat input
        │
        ▼
EmbeddingGenerator.generate_embedding(query)
  Single query text → 384-dim vector
        │
        ▼
PineconeVectorStore.retrieve_similar()
  Cosine similarity search in Pinecone
  Returns top-K matches (default K=5) with:
    - id, score, text chunk, document_id, chunk_index
        │
        ▼
No results? → Return "No relevant information found"
        │
        ▼ (results found)
HuggingFaceLLM.generate_response_with_sources()
  Build prompt:
    "You are a helpful AI assistant...
     Context:
       <chunk_1>
       <chunk_2>
       ...
     Question: <query>
     Answer:"
        │
        ▼
InferenceClient.chat_completion()
  POST to HuggingFace Inference API
  Model: meta-llama/Llama-3.1-8B-Instruct
  max_tokens=512, temperature=0.7, top_p=0.95
        │
        ▼
Response + sources assembled
  sources: [{index, document_id, chunk_index, similarity_score, preview}]
        │
        ▼
Chat history updated in session state
Answer + source citations displayed in UI
```

## 3. REST API Workflow (Optional Backend)

```
HTTP POST /api/documents/upload
        │
        ▼
File saved to temp location
        │
        ▼
DocumentService.upload_and_index()
  → same as ingestion pipeline above
        │
        ▼
Returns DocumentResponse JSON

─────────────────────────────────

HTTP POST /api/qa
  { "query": "...", "top_k": 5 }
        │
        ▼
QAService.answer_query()
  → same as RAG pipeline above
        │
        ▼
Returns QueryResponse JSON with sources

─────────────────────────────────

HTTP DELETE /api/documents/{document_id}
        │
        ▼
DocumentService.delete_document()
        │
        ▼
PineconeVectorStore.delete_document()
  Filter delete: metadata.document_id == id
        │
        ▼
Vectors removed from Pinecone
Local registry entry removed
```

## 4. Configuration Loading Order

```
Environment Variables (.env file)
        │ (loaded by python-dotenv at import time)
        ▼
app/config.py constants
        │
        ▼
validate_config() called on startup
  Raises ConfigError if any required key is missing:
    - PINECONE_API_KEY
    - PINECONE_ENVIRONMENT  
    - HUGGINGFACE_API_TOKEN
```

## 5. Chunk Size and Overlap Behaviour

| Parameter | Default | Effect |
|---|---|---|
| `CHUNK_SIZE` | 500 chars | Maximum characters per chunk |
| `CHUNK_OVERLAP` | 50 chars | Characters re-included from end of previous chunk when splitting oversized text |

Chunking algorithm:
1. Split on `\n\n` (paragraph boundaries)
2. Accumulate paragraphs until `CHUNK_SIZE` reached
3. Oversized single paragraphs are hard-split with `CHUNK_OVERLAP` rollback

## 6. Vector ID Scheme

```
{document_stem}_{unix_timestamp}_chunk_{index}

Example: annual_report_1718534400.123_chunk_0
```

This allows multiple uploads of the same filename without collision.
