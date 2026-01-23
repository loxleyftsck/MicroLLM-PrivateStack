# -*- coding: utf-8 -*-
"""
RAG Engine (Retrieval-Augmented Generation)
Lightweight vector store for document retrieval
"""

import numpy as np
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Simple In-Memory Vector Store for RAG
    Optimized for small-to-medium datasets (up to ~100k chunks)
    """
    
    def __init__(self, embedding_fn, dimension: int = 768, storage_path: str = "data/rag_store"):
        self.embedding_fn = embedding_fn
        self.dimension = dimension
        self.storage_path = Path(storage_path)
        
        # In-memory storage
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        
        # Create storage dir
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self.load()
        
    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add document chunks to the store
        """
        if not chunks:
            return 0
            
        logger.info(f"Adding {len(chunks)} chunks to RAG store...")
        
        new_embeddings_list = []
        valid_chunks = []
        
        start_time = time.time()
        
        # Batch generate embeddings
        # Note: If embedding_fn supports batching, use it. Assuming single for now or wrapped.
        for chunk in chunks:
            text = chunk.get('text', '')
            if not text:
                continue
                
            # Generate embedding
            try:
                emb = self.embedding_fn(text)
                
                if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
                    # Per-token embeddings returned (List[List[float]])
                    # Perform mean pooling
                    # logger.info("Performing mean pooling on token embeddings")
                    emb_np = np.array(emb)
                    emb = np.mean(emb_np, axis=0).tolist()
                
                new_embeddings_list.append(emb)
                valid_chunks.append(chunk)
            except Exception as e:
                logger.error(f"Failed to embed chunk: {e}")
                
        if not new_embeddings_list:
            return 0
            
        # Update storage
        new_embs_np = np.array(new_embeddings_list, dtype=np.float32)
        
        if self.embeddings is None:
            self.embeddings = new_embs_np
        else:
            self.embeddings = np.vstack([self.embeddings, new_embs_np])
            
        self.chunks.extend(valid_chunks)
        
        # Auto-save
        self.save()
        
        duration = time.time() - start_time
        logger.info(f"Added {len(valid_chunks)} chunks in {duration:.2f}s")
        
        return len(valid_chunks)
        
    def search(self, query: str, top_k: int = 3, threshold: float = 0.3) -> List[Dict]:
        """
        Retrieve relevant chunks for a query
        """
        if self.embeddings is None or len(self.chunks) == 0:
            return []
            
        # Embed query
        query_emb = self.embedding_fn(query)
        
        # Compute Cosine Similarity
        # (A . B) / (|A| * |B|)
        
        # Norms
        query_norm = np.linalg.norm(query_emb)
        d_norms = np.linalg.norm(self.embeddings, axis=1)
        
        # Avoid division by zero
        d_norms[d_norms < 1e-10] = 1.0
        
        # Dot product
        scores = np.dot(self.embeddings, query_emb) / (d_norms * query_norm)
        
        # Get top-k
        # Sort desc
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score >= threshold:
                chunk = self.chunks[idx].copy()
                chunk['score'] = score
                results.append(chunk)
                
        return results

    def save(self):
        """Save store to disk"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save chunks
            with open(self.storage_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
                
            # Save embeddings
            if self.embeddings is not None:
                np.save(self.storage_path.with_suffix('.npy'), self.embeddings)
                
            logger.info("RAG store saved")
        except Exception as e:
            logger.error(f"Failed to save RAG store: {e}")

    def load(self):
        """Load store from disk"""
        try:
            json_path = self.storage_path.with_suffix('.json')
            npy_path = self.storage_path.with_suffix('.npy')
            
            if json_path.exists() and npy_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.chunks = json.load(f)
                
                self.embeddings = np.load(npy_path)
                logger.info(f"RAG store loaded: {len(self.chunks)} chunks")
            else:
                logger.info("No existing RAG store found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load RAG store: {e}")
            self.chunks = []
            self.embeddings = None

    def clear(self):
        """Clear all data"""
        self.chunks = []
        self.embeddings = None
        self.save()
        logger.info("RAG store cleared")
