"""
Embedding Service Module
Handles embeddings for vector-based retrieval using OpenAI's embedding API.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import os
from pathlib import Path

if TYPE_CHECKING:
    from openai import OpenAI as OpenAIType
else:
    OpenAIType = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class EmbeddingService:
    """Service for generating embeddings using OpenAI API"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedding service
        
        Args:
            model: Embedding model to use (default: text-embedding-3-small)
        """
        self.model = model
        self.client = None
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and OpenAI is not None:
            self.client = OpenAI(api_key=api_key)
    
    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding or None if service is unavailable
        """
        if not self.client:
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error embedding text: {e}")
            return None
    
    def embed_documents(self, documents: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple documents
        
        Args:
            documents: List of documents to embed
            
        Returns:
            List of vector embeddings (None for failed documents)
        """
        if not self.client or not documents:
            return [None] * len(documents)
        
        # Filter out empty documents
        valid_docs = [doc for doc in documents if doc and doc.strip()]
        if not valid_docs:
            return [None] * len(documents)
        
        try:
            response = self.client.embeddings.create(
                input=valid_docs,
                model=self.model
            )
            # Map embeddings back to original documents maintaining order
            embeddings = {item.index: item.embedding for item in response.data}
            return [
                embeddings.get(valid_docs.index(doc))
                if doc and doc.strip() else None
                for doc in documents
            ]
        except Exception as e:
            print(f"Error embedding documents: {e}")
            return [None] * len(documents)
