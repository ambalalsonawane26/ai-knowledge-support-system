# Limitations — AI Knowledge & Decision Support System

## 1. No Persistent Document Registry

**What it means**: The `DocumentService.documents` dict and `st.session_state.indexed_documents` list live entirely in memory. Restarting the application or refreshing the browser loses the list of what was uploaded and when.

**Impact**: Users cannot see previously indexed documents after a restart. Vectors remain in Pinecone but there is no local record.

**Workaround**: Pinecone itself retains all vectors; documents are still searchable even after restart. A future fix would persist the document registry to a database (SQLite, PostgreSQL).

---

## 2. No Authentication or Multi-Tenancy

**What it means**: There is no login system. All users share the same Pinecone index and see results from every document ever uploaded.

**Impact**: Sensitive documents from one user are visible to any other user who asks a related question.

**Workaround**: For internal/single-user deployments this is acceptable. For multi-user production use, add auth (e.g., Streamlit-Authenticator) and namespace Pinecone queries with a user-scoped metadata filter.

---

## 3. HuggingFace Inference API Rate Limits

**What it means**: The LLM call goes to the public HuggingFace Inference API. Free-tier tokens have rate limits and queuing.

**Impact**: Under concurrent load, responses may be slow or return 429 errors. The system has no retry logic.

**Workaround**: Use a paid HuggingFace Inference Endpoint, or switch to a self-hosted model via Ollama.

---

## 4. Embedding Model Runs In-Process

**What it means**: `sentence-transformers/all-MiniLM-L6-v2` is loaded directly into the Streamlit process (~90 MB model weights).

**Impact**: Cold start takes several seconds. On a low-memory instance, this can cause OOM errors when combined with large documents.

**Workaround**: Pre-warm the model with `@st.cache_resource` (already done). For very constrained environments, switch to a remote embedding API.

---

## 5. Chunking is Character-Count Based

**What it means**: Chunks are split at character boundaries, not sentence or semantic boundaries. A sentence can be cut in the middle.

**Impact**: Edge chunks may lose meaning. The `CHUNK_OVERLAP` setting partially mitigates this but does not guarantee semantic completeness.

**Workaround**: Use LangChain's `RecursiveCharacterTextSplitter` or `SentenceTransformersTokenTextSplitter` for better semantic boundaries.

---

## 6. PDF Extraction Quality Varies

**What it means**: PyPDF2 extracts plain text. It does not handle:
- Scanned PDFs (image-only)
- PDFs with complex column layouts
- Tables in PDFs
- PDFs with password protection

**Impact**: Text quality from poorly structured PDFs will be low, leading to poor retrieval results.

**Workaround**: For scanned PDFs, add OCR (pytesseract is included as a dependency). For tables, use `pdfplumber` or `camelot`.

---

## 7. No Conversation Memory

**What it means**: Each question is answered independently. The LLM does not see previous questions and answers.

**Impact**: Follow-up questions like "Expand on that" or "What about the second point?" do not work as expected.

**Workaround**: Pass the last N chat turns as additional context in the LLM prompt.

---

## 8. Single Pinecone Index

**What it means**: All documents from all users go into one index. Filtering is done via metadata (`document_id`).

**Impact**: Index storage grows indefinitely. Pinecone free tier is limited to ~100K vectors / 1 namespace.

**Workaround**: Implement document deletion after sessions end. Use Pinecone namespaces for logical separation.

---

## 9. Document Deletion Not Wired in UI

**What it means**: The "Delete" button in the Manage Documents tab shows "coming soon". Deletion works in the backend API (`DELETE /api/documents/{id}`) but not in the Streamlit frontend.

**Impact**: Users cannot remove documents via the UI; they accumulate in Pinecone.

---

## 10. Large Files Can Cause Timeouts

**What it means**: A 100 MB PDF with thousands of pages will spend significant time in parsing, chunking, and embedding—all synchronously in the Streamlit request/response cycle.

**Impact**: Browser may appear frozen. Streamlit has no background task support by default.

**Workaround**: Reduce `MAX_UPLOAD_SIZE_MB`, or offload indexing to a background worker (Celery, RQ).

---

## 11. CORS_ORIGINS Parsing

**What it means**: `CORS_ORIGINS` in `config.py` is read as a raw string (e.g. `"['http://localhost:3000']"`) but passed to FastAPI as-is. FastAPI's CORS middleware expects a Python list.

**Impact**: CORS may not be correctly configured for the FastAPI backend.

**Status**: Fixed in production config — see `backend/api.py` which uses `allow_origins=["*"]` as a safe fallback while the config parsing is resolved.
