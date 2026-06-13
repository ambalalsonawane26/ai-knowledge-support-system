"""
Document processing module for handling multiple file formats
Supports PDF, TXT, CSV, and Excel files
"""

import os
import logging
from typing import List, Dict, Tuple
from pathlib import Path
import PyPDF2
import pandas as pd
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents from multiple formats"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: str) -> Tuple[List[str], Dict]:
        """
        Process a file and return chunks and metadata
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Tuple of (chunks, metadata)
        """
        file_ext = Path(file_path).suffix.lower().strip('.')
        
        if file_ext == 'pdf':
            return self._process_pdf(file_path)
        elif file_ext == 'txt':
            return self._process_text(file_path)
        elif file_ext == 'csv':
            return self._process_csv(file_path)
        elif file_ext in ['xlsx', 'xls']:
            return self._process_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _process_pdf(self, file_path: str) -> Tuple[List[str], Dict]:
        """Process PDF file"""
        logger.info(f"Processing PDF file: {file_path}")
        chunks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                
                chunks = self._chunk_text(full_text)
                
                metadata = {
                    "file_type": "pdf",
                    "file_name": os.path.basename(file_path),
                    "total_pages": total_pages,
                    "total_chunks": len(chunks),
                    "character_count": len(full_text)
                }
                
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
        
        return chunks, metadata
    
    def _process_text(self, file_path: str) -> Tuple[List[str], Dict]:
        """Process plain text file"""
        logger.info(f"Processing text file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            chunks = self._chunk_text(content)
            
            metadata = {
                "file_type": "txt",
                "file_name": os.path.basename(file_path),
                "total_chunks": len(chunks),
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise
        
        return chunks, metadata
    
    def _process_csv(self, file_path: str) -> Tuple[List[str], Dict]:
        """Process CSV file"""
        logger.info(f"Processing CSV file: {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            
            # Convert dataframe to text format
            content = ""
            content += "CSV File Content\n"
            content += f"Columns: {', '.join(df.columns)}\n"
            content += f"Rows: {len(df)}\n\n"
            
            # Add row data
            for idx, row in df.iterrows():
                content += f"Row {idx + 1}:\n"
                for col in df.columns:
                    content += f"  {col}: {row[col]}\n"
                content += "\n"
            
            chunks = self._chunk_text(content)
            
            metadata = {
                "file_type": "csv",
                "file_name": os.path.basename(file_path),
                "total_rows": len(df),
                "columns": list(df.columns),
                "total_chunks": len(chunks),
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {str(e)}")
            raise
        
        return chunks, metadata
    
    def _process_excel(self, file_path: str) -> Tuple[List[str], Dict]:
        """Process Excel file"""
        logger.info(f"Processing Excel file: {file_path}")
        
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            
            content = ""
            sheet_info = {}
            
            for sheet in sheets:
                df = pd.read_excel(file_path, sheet_name=sheet)
                
                content += f"\n=== Sheet: {sheet} ===\n"
                content += f"Columns: {', '.join(df.columns)}\n"
                content += f"Rows: {len(df)}\n\n"
                
                for idx, row in df.iterrows():
                    content += f"Row {idx + 1}:\n"
                    for col in df.columns:
                        content += f"  {col}: {row[col]}\n"
                    content += "\n"
                
                sheet_info[sheet] = {
                    "columns": list(df.columns),
                    "rows": len(df)
                }
            
            chunks = self._chunk_text(content)
            
            metadata = {
                "file_type": "xlsx",
                "file_name": os.path.basename(file_path),
                "sheets": sheets,
                "sheet_info": sheet_info,
                "total_chunks": len(chunks),
                "character_count": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel file {file_path}: {str(e)}")
            raise
        
        return chunks, metadata
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by sentences or paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Ensure no chunk is too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.chunk_size:
                # Split large chunks further
                sub_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_large_chunk(self, text: str) -> List[str]:
        """Split a large chunk into smaller pieces with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
        
        return chunks
