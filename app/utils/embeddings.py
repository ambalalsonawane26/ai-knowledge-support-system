"""
Embedding generation module using Sentence Transformers
"""

import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using Sentence Transformers"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding generator
        
        Args:
            model_name: Name of the sentence transformer model
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=False)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        return self.embedding_dim
