"""
Pinecone vector store integration for semantic search
"""

import logging
from typing import List, Dict, Tuple
import pinecone
from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from app.utils.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)


class PineconeVectorStore:
    """Manage document embeddings and retrieval using Pinecone"""
    
    def __init__(self):
        """Initialize Pinecone connection"""
        logger.info("Initializing Pinecone Vector Store")
        
        # Initialize Pinecone client and target the index by name.
        self.index_name = PINECONE_INDEX_NAME
        self.pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(self.index_name)
        
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator()
        
        logger.info(f"Connected to Pinecone index: {self.index_name}")
    
    def upsert_documents(self, 
                        documents: List[str], 
                        document_id: str,
                        metadata: Dict = None) -> bool:
        """
        Upload documents to Pinecone
        
        Args:
            documents: List of document chunks
            document_id: Unique identifier for the document
            metadata: Optional metadata to store with vectors
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Upserting {len(documents)} chunks for document: {document_id}")
            
            # Generate embeddings for all documents
            embeddings = self.embedding_generator.generate_embeddings_batch(documents)
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector_id = f"{document_id}_chunk_{idx}"
                vector_metadata = {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "text": doc,
                }
                
                if metadata:
                    vector_metadata.update(metadata)
                
                vectors_to_upsert.append((
                    vector_id,
                    embedding,
                    vector_metadata
                ))
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Successfully upserted {len(vectors_to_upsert)} vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error upserting documents: {str(e)}")
            raise
    
    def retrieve_similar(self, 
                        query: str, 
                        top_k: int = 5,
                        filter: Dict = None) -> List[Dict]:
        """
        Retrieve similar documents for a query
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents with scores
        """
        try:
            logger.info(f"Retrieving similar documents for query with top_k={top_k}")
            
            # Generate embedding for query
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            # Format results
            retrieved_docs = []
            for match in results.matches:
                retrieved_docs.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "document_id": match.metadata.get("document_id", ""),
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "metadata": match.metadata
                })
            
            logger.info(f"Retrieved {len(retrieved_docs)} similar documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving similar documents: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all vectors associated with a document
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Deleting document: {document_id}")
            
            # Delete by metadata filter
            self.index.delete(
                filter={"document_id": {"$eq": document_id}}
            )
            
            logger.info(f"Successfully deleted document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_document_stats(self, document_id: str) -> Dict:
        """
        Get statistics about a document in the vector store
        
        Args:
            document_id: ID of document
            
        Returns:
            Dictionary with document stats
        """
        try:
            # Query to find vectors for this document
            results = self.index.query(
                vector=[0] * self.embedding_generator.get_embedding_dimension(),
                top_k=10000,
                include_metadata=True,
                filter={"document_id": {"$eq": document_id}}
            )
            
            stats = {
                "document_id": document_id,
                "total_chunks": len(results.matches),
                "vector_dimension": self.embedding_generator.get_embedding_dimension()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            raise
    
    def clear_index(self) -> bool:
        """Delete all vectors from the index (use with caution)"""
        try:
            logger.warning("Clearing entire Pinecone index")
            self.index.delete(delete_all=True)
            return True
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
            raise
