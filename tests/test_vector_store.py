"""
Tests for Pinecone vector store integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.utils.vector_store import PineconeVectorStore


@pytest.fixture
@patch('app.utils.vector_store.pinecone.Pinecone')
def vector_store(mock_pinecone):
    """Mock Pinecone connection"""
    # Mock the Pinecone client and its index targeter
    mock_index_instance = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.Index.return_value = mock_index_instance
    mock_pinecone.return_value = mock_client_instance

    return PineconeVectorStore()


def test_vector_store_initialization():
    """Test vector store initialization"""
    with patch('app.utils.vector_store.pinecone.Pinecone') as mock_pinecone:
        mock_client_instance = MagicMock()
        mock_client_instance.Index.return_value = MagicMock()
        mock_pinecone.return_value = mock_client_instance
        store = PineconeVectorStore()
        assert store.index_name is not None


def test_embedding_dimension():
    """Test embedding dimension"""
    with patch('app.utils.vector_store.pinecone.Pinecone') as mock_pinecone:
        mock_client_instance = MagicMock()
        mock_client_instance.Index.return_value = MagicMock()
        mock_pinecone.return_value = mock_client_instance
        store = PineconeVectorStore()
        dim = store.embedding_generator.get_embedding_dimension()
        assert dim > 0
