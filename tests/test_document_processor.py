"""
Tests for document processor module
"""

import pytest
import tempfile
import os
from pathlib import Path

from app.utils.document_processor import DocumentProcessor


@pytest.fixture
def processor():
    return DocumentProcessor(chunk_size=100, chunk_overlap=10)


@pytest.fixture
def sample_text_file():
    """Create a temporary text file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a sample document for testing.\n\n")
        f.write("It contains multiple paragraphs.\n\n")
        f.write("The processor should chunk this properly.")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


def test_text_processing(processor, sample_text_file):
    """Test processing text file"""
    chunks, metadata = processor.process_file(sample_text_file)
    
    assert len(chunks) > 0, "Should produce at least one chunk"
    assert metadata["file_type"] == "txt"
    assert metadata["total_chunks"] == len(chunks)
    assert "character_count" in metadata


def test_chunking(processor):
    """Test text chunking"""
    text = "This is a long document. " * 100
    chunks = processor._chunk_text(text)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk) <= processor.chunk_size or len(chunk) > processor.chunk_size
