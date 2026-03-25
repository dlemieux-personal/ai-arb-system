"""Vector memory module for embeddings and semantic search"""

from src.vector_memory.embedding_service import EmbeddingService
from src.vector_memory.vector_store import VectorStore
from src.vector_memory.vector_store_factory import (
    create_vector_store,
    get_vector_store,
    close_vector_store
)
from src.vector_memory.retrieval_service import RetrievalService

__all__ = [
    'EmbeddingService',
    'VectorStore',
    'create_vector_store',
    'get_vector_store',
    'close_vector_store',
    'RetrievalService',
]

