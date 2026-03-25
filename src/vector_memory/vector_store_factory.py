"""
Vector Store Factory Module
Factory for creating and managing VectorStore instances.
"""

import os
from typing import Optional
from src.vector_memory.vector_store import VectorStore
from src.vector_memory.embedding_service import EmbeddingService

# Global vector store instance
_vector_store: Optional[VectorStore] = None


def create_vector_store(collection_name: Optional[str] = None,
                       persist_dir: Optional[str] = None,
                       embedding_model: Optional[str] = None) -> VectorStore:
    """
    Create a new VectorStore instance
    
    Args:
        collection_name: Name of the vector collection
        persist_dir: Directory for persistent storage
        embedding_model: Embedding model name
        
    Returns:
        VectorStore instance
    """
    collection_name = collection_name or os.getenv('CHROMADB_COLLECTION_NAME', 'architecture_reviews')
    persist_dir = persist_dir or os.getenv('CHROMADB_PERSIST_DIR', './memory/embeddings_cache')
    embedding_model = embedding_model or 'text-embedding-3-small'
    
    embedding_service = EmbeddingService(model=embedding_model)
    vector_store = VectorStore(
        collection_name=collection_name,
        persist_dir=persist_dir,
        embedding_service=embedding_service
    )
    
    return vector_store


def get_vector_store() -> Optional[VectorStore]:
    """
    Get the global vector store instance, creating it if necessary
    
    Returns:
        VectorStore instance or None if creation failed
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = create_vector_store()
    
    return _vector_store


def close_vector_store() -> None:
    """Close and cleanup the vector store"""
    global _vector_store
    if _vector_store is not None:
        # ChromaDB doesn't require explicit cleanup for PersistentClient
        _vector_store = None
