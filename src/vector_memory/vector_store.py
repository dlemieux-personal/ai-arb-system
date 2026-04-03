"""
Vector Store Module
Manages vector storage and similarity search using ChromaDB.
"""

import uuid
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
    import chromadb
    from chromadb.config import Settings
else:
    chromadb = None  # type: ignore
    Settings = None  # type: ignore

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None  # type: ignore
    Settings = None  # type: ignore

from src.vector_memory.embedding_service import EmbeddingService


class VectorStore:
    """Vector store using ChromaDB for similarity search on embeddings"""
    
    def __init__(self, collection_name: str, persist_dir: Optional[str] = None,
                 embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize vector store
        
        Args:
            collection_name: Name of the vector collection
            persist_dir: Directory for persistent storage
            embedding_service: Optional EmbeddingService instance
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir or os.getenv('CHROMADB_PERSIST_DIR', './memory/embeddings')
        self.embedding_service = embedding_service or EmbeddingService()
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize ChromaDB client and collection"""
        if chromadb is None:
            return
        
        try:
            # Create persist directory if needed
            if self.persist_dir:
                Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
                # Initialize persistent client
                self.client = chromadb.PersistentClient(
                    path=self.persist_dir
                )
            else:
                # Use in-memory client
                self.client = chromadb.Client()
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None,
                     ids: Optional[List[str]] = None) -> None:
        """
        Add documents to vector store
        
        Args:
            documents: List of documents
            metadatas: Optional metadata for each document
            ids: Optional document IDs
        """
        if not self.collection or not documents:
            return
        
        # Generate UUIDs if ids not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(documents)
        
        # Filter out documents with failed embeddings
        valid_items = []
        for idx, (doc, embedding, doc_id) in enumerate(zip(documents, embeddings, ids)):
            if embedding is not None:
                meta = {}
                if metadatas and idx < len(metadatas):
                    meta = metadatas[idx]
                
                valid_items.append({
                    'id': doc_id,
                    'embedding': embedding,
                    'document': doc,
                    'metadata': meta
                })
        
        if valid_items:
            try:
                self.collection.add(
                    ids=[item['id'] for item in valid_items],
                    embeddings=[item['embedding'] for item in valid_items],
                    documents=[item['document'] for item in valid_items],
                    metadatas=[item['metadata'] for item in valid_items]
                )
            except Exception as e:
                print(f"Error adding documents to ChromaDB: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self.collection or not query or not query.strip():
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        if query_embedding is None:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Format results
            documents = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            ids = results.get('ids', [[]])[0]
            
            formatted_results = []
            for doc_id, doc, distance, metadata in zip(ids, documents, distances, metadatas):
                # Convert distance to similarity (cosine distance -> similarity)
                # Distance is already 0-2 range, convert 1 - distance/2 for similarity 0-1
                similarity = 1 - (distance / 2) if distance is not None else 0
                formatted_results.append({
                    'id': doc_id,
                    'document': doc,
                    'similarity': max(0, min(1, similarity)),
                    'metadata': metadata or {}
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []
    
    def delete(self, ids: List[str]) -> None:
        """
        Delete documents from vector store
        
        Args:
            ids: List of document IDs to delete
        """
        if not self.collection or not ids:
            return
        
        try:
            self.collection.delete(ids=ids)
        except Exception as e:
            print(f"Error deleting from ChromaDB: {e}")
    
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve documents by ID
        
        Args:
            ids: List of document IDs
            
        Returns:
            List of documents
        """
        if not self.collection or not ids:
            return []
        
        try:
            results = self.collection.get(ids=ids)
            
            documents = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            retrieved_ids = results.get('ids', [])
            
            return [
                {
                    'id': doc_id,
                    'document': doc,
                    'metadata': meta or {}
                }
                for doc_id, doc, meta in zip(retrieved_ids, documents, metadatas)
            ]
        except Exception as e:
            print(f"Error retrieving from ChromaDB: {e}")
            return []
