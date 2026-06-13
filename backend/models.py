"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    file_name: str = Field(..., description="Name of the file")
    file_type: str = Field(..., description="Type of file (pdf, txt, csv, xlsx)")
    tags: Optional[List[str]] = Field(default=None, description="Tags for the document")


class DocumentResponse(BaseModel):
    """Response model for document operations"""
    document_id: str
    file_name: str
    file_type: str
    total_chunks: int
    uploaded_at: datetime
    status: str


class QueryRequest(BaseModel):
    """Request model for Q&A"""
    query: str = Field(..., min_length=1, description="The question to answer")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")


class SourceDocument(BaseModel):
    """Model for source document in response"""
    index: int
    document_id: str
    chunk_index: int
    similarity_score: float
    preview: str


class QueryResponse(BaseModel):
    """Response model for Q&A"""
    response: str
    query: str
    sources: List[SourceDocument]
    model: str
    status: str
    error: Optional[str] = None


class ConversationMessage(BaseModel):
    """Model for conversation message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: Optional[List[SourceDocument]] = None


class ConversationResponse(BaseModel):
    """Response model for conversation"""
    conversation_id: str
    messages: List[ConversationMessage]
    created_at: datetime
    updated_at: datetime


class DocumentMetadata(BaseModel):
    """Model for document metadata"""
    document_id: str
    file_name: str
    file_type: str
    total_chunks: int
    character_count: int
    uploaded_at: datetime
    metadata: Optional[Dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    components: Dict[str, str]
