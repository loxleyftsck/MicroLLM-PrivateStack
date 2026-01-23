# -*- coding: utf-8 -*-
"""
Document Processor for RAG
Handles text extraction (PDF/TXT) and smart chunking
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
import io

# Optional imports
try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Process documents for RAG ingestion:
    1. Extract text from various formats
    2. clean and normalize text
    3. Smart chunking with overlap
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size  # Approx characters/tokens
        self.chunk_overlap = chunk_overlap
        
    def process_file(self, file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        """
        Process a file and return list of chunks
        """
        ext = Path(filename).suffix.lower()
        text = ""
        
        try:
            if ext == '.pdf':
                text = self._extract_pdf(file_content)
            elif ext in ['.txt', '.md', '.csv', '.json']:
                text = file_content.decode('utf-8', errors='ignore')
            else:
                logger.warning(f"Unsupported file type: {ext}")
                return []
                
            if not text:
                logger.warning(f"No text extracted from {filename}")
                return []
                
            # Chunk the text
            chunks = self._create_chunks(text)
            
            # Format results
            return [
                {
                    'text': chunk,
                    'source': filename,
                    'chunk_id': i,
                    'timestamp': 0  # To be filled by storage
                }
                for i, chunk in enumerate(chunks)
            ]
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return []

    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF bytes"""
        if not PDF_AVAILABLE:
            logger.error("pypdf not installed")
            return ""
            
        try:
            pdf_file = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)
            text = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            
            return "\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""

    def _create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        Uses simple character count (fast) but respects sentence boundaries roughly
        """
        chunks = []
        if not text:
            return []
            
        # Clean text slightly
        text = " ".join(text.split())
        
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # If we are not at the end of text, try to find a sentence break
            if end < text_len:
                # Look for last period/sentence end within the last 20% of the chunk
                # to avoid breaking sentences in the middle
                search_window = text[int(end - self.chunk_size*0.2):end]
                last_period = max(
                    search_window.rfind('. '), 
                    search_window.rfind('? '), 
                    search_window.rfind('! '),
                    search_window.rfind('\n')
                )
                
                if last_period != -1:
                    # Adjust end to the found period (relative to search_window start)
                    end = int(end - self.chunk_size*0.2) + last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start forward by chunk_size minus overlap
            start = end - self.chunk_overlap
            
            # Ensure we always move forward
            if start >= end:
                start = end
        
        return chunks
