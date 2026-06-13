"""
Question Answering service
"""

import logging
from typing import Dict, List

from app.utils.vector_store import PineconeVectorStore
from app.utils.llm_handler import HuggingFaceLLM

logger = logging.getLogger(__name__)


class QAService:
    """Service for question answering operations"""
    
    def __init__(self):
        self.vector_store = PineconeVectorStore()
        self.llm = HuggingFaceLLM()
        self.conversations: Dict[str, List[Dict]] = {}
    
    def answer_query(self, query: str, top_k: int = 5, context_only: bool = False) -> Dict:
        """
        Answer a user query
        
        Args:
            query: The question
            top_k: Number of relevant documents to retrieve
            context_only: If True, return only context without LLM response
            
        Returns:
            Response with answer and sources
        """
        try:
            logger.info(f"Processing query: {query[:50]}...")
            
            # Retrieve relevant documents
            retrieved = self.vector_store.retrieve_similar(
                query=query,
                top_k=top_k
            )
            
            if context_only:
                return {
                    "query": query,
                    "context_chunks": retrieved,
                    "context_only": True
                }
            
            if not retrieved:
                return {
                    "response": "No relevant information found in the documents.",
                    "query": query,
                    "sources": [],
                    "status": "no_context"
                }
            
            # Generate response
            result = self.llm.generate_response_with_sources(
                query=query,
                retrieved_docs=retrieved
            )
            
            result["status"] = "success"
            return result
            
        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "query": query,
                "status": "error",
                "error": str(e)
            }
    
    def start_conversation(self, conversation_id: str) -> Dict:
        """Start a new conversation"""
        self.conversations[conversation_id] = []
        return {"conversation_id": conversation_id, "messages": []}
    
    def add_message(self, conversation_id: str, role: str, content: str, sources: List = None) -> Dict:
        """Add a message to conversation"""
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)
        
        message = {
            "role": role,
            "content": content,
            "sources": sources or []
        }
        
        self.conversations[conversation_id].append(message)
        return message
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        return self.conversations.get(conversation_id, [])
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant documents without generating response"""
        logger.info(f"Searching documents for: {query}")
        return self.vector_store.retrieve_similar(query=query, top_k=top_k)
