"""
FastAPI backend for AI Knowledge Support System (Optional)
Run with: uvicorn backend.api:app --reload
"""

import logging
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from backend.models import (
    QueryRequest, QueryResponse, DocumentResponse,
    DocumentUploadRequest, HealthResponse, SourceDocument
)
from backend.services.document_service import DocumentService
from backend.services.qa_service import QAService
from app.config import CORS_ORIGINS, API_HOST, API_PORT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Knowledge Support System API",
    description="REST API for document Q&A system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
qa_service = QAService()


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint"""
    return {
        "name": "AI Knowledge Support System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        components={
            "api": "running",
            "document_service": "running",
            "qa_service": "running"
        }
    )


@app.post("/api/documents/upload", response_model=DocumentResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    tags: List[str] = None
):
    """Upload and index a new document"""
    try:
        # Save file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Index document
        doc_info = document_service.upload_and_index(tmp_path, tags)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return DocumentResponse(
            document_id=doc_info["document_id"],
            file_name=doc_info["file_name"],
            file_type=doc_info["file_type"],
            total_chunks=doc_info["total_chunks"],
            uploaded_at=doc_info["uploaded_at"],
            status="indexed"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/documents", tags=["Documents"])
def list_documents():
    """List all indexed documents"""
    try:
        documents = document_service.list_documents()
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}", tags=["Documents"])
def get_document(document_id: str):
    """Get document information"""
    try:
        doc = document_service.get_document_info(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{document_id}", tags=["Documents"])
def delete_document(document_id: str):
    """Delete a document"""
    try:
        success = document_service.delete_document(document_id)
        if success:
            return {"message": "Document deleted successfully", "document_id": document_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa", response_model=QueryResponse, tags=["Q&A"])
def ask_question(request: QueryRequest):
    """Ask a question and get an answer"""
    try:
        result = qa_service.answer_query(
            query=request.query,
            top_k=request.top_k
        )
        
        # Format sources
        sources = []
        for source in result.get("sources", []):
            sources.append(SourceDocument(
                index=source["index"],
                document_id=source["document_id"],
                chunk_index=source["chunk_index"],
                similarity_score=source["similarity_score"],
                preview=source["preview"]
            ))
        
        return QueryResponse(
            response=result.get("response", "No response generated"),
            query=request.query,
            sources=sources,
            model=result.get("model", "unknown"),
            status=result.get("status", "unknown"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search", tags=["Q&A"])
def search_documents(request: QueryRequest):
    """Search for relevant documents"""
    try:
        results = qa_service.search_documents(
            query=request.query,
            top_k=request.top_k
        )
        return {"query": request.query, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/search/tags/{tag}", tags=["Documents"])
def get_documents_by_tag(tag: str):
    """Get documents with a specific tag"""
    try:
        docs = document_service.get_documents_by_tag(tag)
        return {"tag": tag, "documents": docs, "count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
