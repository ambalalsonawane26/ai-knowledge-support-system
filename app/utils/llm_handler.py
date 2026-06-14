"""
LLM handler for generating responses using Hugging Face models
"""

import logging
from typing import List, Dict
from huggingface_hub import InferenceClient
from app.config import HUGGINGFACE_API_TOKEN, LLM_MODEL_NAME

logger = logging.getLogger(__name__)


class HuggingFaceLLM:
    """Generate responses using Hugging Face LLM"""
    
    def __init__(self, model_name: str = LLM_MODEL_NAME):
        """
        Initialize Hugging Face LLM
        
        Args:
            model_name: Name of the Hugging Face model to use
        """
        logger.info(f"Initializing Hugging Face LLM: {model_name}")
        
        self.model_name = model_name
        self.client = InferenceClient(
            model=model_name,
            token=HUGGINGFACE_API_TOKEN
        )
        
        logger.info(f"Hugging Face LLM initialized successfully")
    
    def generate_response(self,
                         query: str,
                         context: List[str],
                         max_length: int = 512,
                         temperature: float = 0.7) -> Dict:
        """
        Generate a response based on query and context
        
        Args:
            query: User's question
            context: List of relevant document chunks
            max_length: Maximum length of response
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            logger.info(f"Generating response for query: {query[:50]}...")
            
            # Prepare context
            context_text = "\n\n".join(context)
            
            # Create prompt
            prompt = self._create_prompt(query, context_text)
            
            # Generate response
            completion = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length,
                temperature=temperature,
                top_p=0.95,
            )
            response = completion.choices[0].message.content

            result = {
                "response": response,
                "query": query,
                "context_used": len(context),
                "model": self.model_name,
                "status": "success"
            }
            
            logger.info(f"Response generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "response": "I encountered an error while generating a response. Please try again.",
                "query": query,
                "error": str(e),
                "status": "error"
            }
    
    def generate_response_with_sources(self,
                                       query: str,
                                       retrieved_docs: List[Dict],
                                       max_length: int = 512) -> Dict:
        """
        Generate response with source citations
        
        Args:
            query: User's question
            retrieved_docs: List of retrieved documents with metadata
            max_length: Maximum length of response
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        try:
            logger.info(f"Generating grounded response with sources")
            
            # Extract context chunks
            context_chunks = [doc["text"] for doc in retrieved_docs]
            
            # Generate response
            response_data = self.generate_response(
                query=query,
                context=context_chunks,
                max_length=max_length
            )
            
            # Add source information
            sources = []
            for i, doc in enumerate(retrieved_docs):
                sources.append({
                    "index": i + 1,
                    "document_id": doc.get("document_id", "unknown"),
                    "chunk_index": doc.get("chunk_index", 0),
                    "similarity_score": doc.get("score", 0),
                    "preview": doc.get("text", "")[:200] + "..."
                })
            
            response_data["sources"] = sources
            response_data["grounded"] = True
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating grounded response: {str(e)}")
            return {
                "response": "Error generating grounded response.",
                "query": query,
                "error": str(e),
                "status": "error",
                "grounded": False
            }
    
    def _create_prompt(self, query: str, context: str) -> str:
        """
        Create a prompt for the LLM
        
        Args:
            query: User's question
            context: Context information
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful AI assistant that answers questions based on provided context.

Context:
{context}

Question: {query}

Answer: """
        
        return prompt
    
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Summarize a text
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        try:
            logger.info("Generating summary")
            
            prompt = f"Summarize the following text in {max_length} words:\n\n{text}\n\nSummary:"

            completion = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_length
            )

            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise
    
    def answer_question(self,
                       question: str,
                       context: str,
                       system_prompt: str = None) -> str:
        """
        Simple question answering
        
        Args:
            question: The question to answer
            context: Context for answering
            system_prompt: Optional custom system prompt
            
        Returns:
            Answer text
        """
        try:
            if system_prompt is None:
                system_prompt = "You are a helpful assistant. Answer the question based on the provided context."
            
            prompt = f"{system_prompt}\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"

            completion = self.client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256
            )

            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise
