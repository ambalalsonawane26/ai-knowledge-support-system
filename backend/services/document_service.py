"""
Document management service
"""

import logging
import os
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from app.utils.document_processor import DocumentProcessor
from app.utils.vector_store import PineconeVectorStore

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management operations"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = PineconeVectorStore()
        self.documents: Dict[str, Dict] = {}
    
    def upload_and_index(self, file_path: str, tags: List[str] = None) -> Dict:
        """
        Upload and index a document
        
        Args:
            file_path: Path to the document file
            tags: Optional tags for the document
            
        Returns:
            Document metadata
        """
        try:
            logger.info(f"Uploading and indexing: {file_path}")
            
            # Process document
            chunks, metadata = self.processor.process_file(file_path)
            
            # Generate document ID
            doc_id = f"{Path(file_path).stem}_{datetime.now().timestamp()}"
            
            # Add tags to metadata
            if tags:
                metadata["tags"] = tags
            
            # Upsert to vector store
            self.vector_store.upsert_documents(
                documents=chunks,
                document_id=doc_id,
                metadata=metadata
            )
            
            # Store document info
            self.documents[doc_id] = {
                "document_id": doc_id,
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": Path(file_path).suffix.lower().strip('.'),
                "total_chunks": len(chunks),
                "uploaded_at": datetime.now(),
                "tags": tags or [],
                "metadata": metadata
            }
            
            logger.info(f"Document {doc_id} indexed successfully")
            return self.documents[doc_id]
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting document: {document_id}")
            
            # Delete from vector store
            self.vector_store.delete_document(document_id)
            
            # Remove from local registry
            if document_id in self.documents:
                del self.documents[document_id]
            
            logger.info(f"Document {document_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_document_info(self, document_id: str) -> Dict:
        """Get information about a document"""
        if document_id in self.documents:
            return self.documents[document_id]
        return None
    
    def list_documents(self) -> List[Dict]:
        """List all documents"""
        return list(self.documents.values())
    
    def get_documents_by_tag(self, tag: str) -> List[Dict]:
        """Get documents with a specific tag"""
        return [
            doc for doc in self.documents.values()
            if tag in doc.get("tags", [])
        ]
