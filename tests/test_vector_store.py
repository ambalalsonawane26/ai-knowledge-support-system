"""
Tests for Pinecone vector store integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.utils.vector_store import PineconeVectorStore


@pytest.fixture
@patch('app.utils.vector_store.pinecone.init')
@patch('app.utils.vector_store.pinecone.Index')
def vector_store(mock_index, mock_init):
    """Mock Pinecone connection"""
    # Mock the index
    mock_index_instance = MagicMock()
    mock_index.return_value = mock_index_instance
    
    return PineconeVectorStore()


def test_vector_store_initialization():
    """Test vector store initialization"""
    with patch('app.utils.vector_store.pinecone.init'):
        with patch('app.utils.vector_store.pinecone.Index'):
            store = PineconeVectorStore()
            assert store.index_name is not None


def test_embedding_dimension():
    """Test embedding dimension"""
    with patch('app.utils.vector_store.pinecone.init'):
        with patch('app.utils.vector_store.pinecone.Index'):
            store = PineconeVectorStore()
            dim = store.embedding_generator.get_embedding_dimension()
            assert dim > 0
