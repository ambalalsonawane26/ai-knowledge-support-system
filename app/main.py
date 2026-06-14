"""
Main Streamlit application for AI Knowledge and Decision Support System
"""

import streamlit as st
import logging
import os
from datetime import datetime
from pathlib import Path

from app.config import (
    STREAMLIT_CONFIG, UPLOAD_FOLDER, validate_config,
    MAX_UPLOAD_SIZE_MB, SUPPORTED_FILE_TYPES, TOP_K_RETRIEVAL
)
from app.utils.document_processor import DocumentProcessor
from app.utils.vector_store import PineconeVectorStore
from app.utils.llm_handler import HuggingFaceLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG["page_config"])

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stChat {
        max-width: 900px;
        margin: auto;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize system components (cached)"""
    try:
        validate_config()
        vector_store = PineconeVectorStore()
        llm = HuggingFaceLLM()
        processor = DocumentProcessor()
        return {
            "vector_store": vector_store,
            "llm": llm,
            "processor": processor,
            "initialized": True
        }
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        return {"initialized": False}


def save_upload_file(uploaded_file) -> str:
    """Save uploaded file and return path"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None


def process_and_index_document(file_path: str, system: dict) -> bool:
    """Process document and index it in Pinecone"""
    try:
        with st.spinner(f"Processing {Path(file_path).name}..."):
            processor = system["processor"]
            vector_store = system["vector_store"]
            
            # Process document
            chunks, metadata = processor.process_file(file_path)
            
            # Generate document ID
            doc_id = f"{Path(file_path).stem}_{datetime.now().timestamp()}"
            
            # Upsert to Pinecone
            vector_store.upsert_documents(
                documents=chunks,
                document_id=doc_id,
                metadata=metadata
            )
            
            st.success(f"✅ Successfully indexed {len(chunks)} chunks from {Path(file_path).name}")
            return True
            
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        logger.error(f"Document processing error: {str(e)}")
        return False


def answer_question(query: str, system: dict) -> dict:
    """Get answer for a question using RAG pipeline"""
    try:
        vector_store = system["vector_store"]
        llm = system["llm"]
        
        # Retrieve relevant documents
        retrieved = vector_store.retrieve_similar(
            query=query,
            top_k=TOP_K_RETRIEVAL
        )
        
        if not retrieved:
            return {
                "response": "No relevant information found in the documents.",
                "sources": [],
                "error": "No context retrieved"
            }
        
        # Generate response with sources
        result = llm.generate_response_with_sources(
            query=query,
            retrieved_docs=retrieved
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return {
            "response": f"Error: {str(e)}",
            "error": str(e)
        }


def main():
    """Main application"""
    
    # Header
    st.title("🤖 AI Knowledge & Decision Support System")
    st.markdown("Upload documents and ask natural language questions to get AI-powered answers grounded in your data.")
    
    # Initialize system
    system = initialize_system()
    
    if not system.get("initialized"):
        st.error("System initialization failed. Please check your configuration.")
        st.stop()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "❓ Ask Questions", "📊 Manage Documents"])
    
    # Tab 1: Upload Documents
    with tab1:
        st.header("Upload Documents")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **Supported Formats:**
            - 📄 PDF files
            - 📝 Text files (.txt)
            - 📊 CSV files
            - 📈 Excel files (.xlsx, .xls)
            """)
        
        with col2:
            st.markdown(f"""
            **Limits:**
            - Max file size: {MAX_UPLOAD_SIZE_MB}MB
            - Multiple uploads supported
            """)
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=list(SUPPORTED_FILE_TYPES.keys()),
            accept_multiple_files=True,
            help="Upload documents to create a searchable knowledge base"
        )
        
        if uploaded_files:
            st.markdown("---")
            
            if st.button("📥 Process and Index Documents", use_container_width=True):
                progress_bar = st.progress(0)
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    # Validate file size
                    if uploaded_file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                        st.error(f"❌ {uploaded_file.name} exceeds {MAX_UPLOAD_SIZE_MB}MB limit")
                        continue
                    
                    # Save file
                    file_path = save_upload_file(uploaded_file)
                    
                    if file_path:
                        # Process and index
                        success = process_and_index_document(file_path, system)
                        
                        if success:
                            # Store in session state
                            if "indexed_documents" not in st.session_state:
                                st.session_state.indexed_documents = []
                            
                            st.session_state.indexed_documents.append({
                                "name": uploaded_file.name,
                                "size": uploaded_file.size,
                                "indexed_at": datetime.now()
                            })
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
    
    # Tab 2: Ask Questions
    with tab2:
        st.header("❓ Ask Questions")
        
        st.markdown("Enter your question below. The system will search your documents and provide grounded answers.")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                if message.get("sources"):
                    with st.expander("📚 View Sources"):
                        for source in message["sources"]:
                            st.markdown(f"""
                            **Source {source['index']}:**
                            - Document: {source['document_id']}
                            - Similarity: {source['similarity_score']:.2%}
                            - Preview: {source['preview'][:150]}...
                            """)

    # Tab 3: Manage Documents
    with tab3:
        st.header("📊 Manage Documents")
        
        if "indexed_documents" in st.session_state and st.session_state.indexed_documents:
            st.markdown("**Indexed Documents:**")
            
            for doc in st.session_state.indexed_documents:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"📄 **{doc['name']}**")
                    st.caption(f"Size: {doc['size'] / 1024:.2f} KB | Indexed: {doc['indexed_at'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.metric("Status", "✅ Indexed")
                
                with col3:
                    if st.button("🗑️", key=f"delete_{doc['name']}"):
                        st.info(f"Delete feature coming soon for {doc['name']}")
        else:
            st.info("No documents indexed yet. Upload documents in the 'Upload Documents' tab.")
        
        # Clear chat history
        st.markdown("---")
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")

    # Chat input (must live outside tabs/containers per Streamlit constraints)
    user_query = st.chat_input("Ask a question...", key="user_input")

    if user_query:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })

        # Generate response
        with st.spinner("🤔 Thinking..."):
            response_data = answer_question(user_query, system)

        # Add to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_data.get("response", "No response"),
            "sources": response_data.get("sources", [])
        })

        # Rerun so the new messages render inside the chat history on Tab 2
        st.rerun()


if __name__ == "__main__":
    main()
