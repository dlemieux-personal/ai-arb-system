"""
Unit tests for embedding service and vector store
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.vector_memory.embedding_service import EmbeddingService
from src.vector_memory.vector_store import VectorStore


class TestEmbeddingService:
    """Tests for EmbeddingService"""
    
    def test_embedding_service_initialization_without_api_key(self):
        """Test initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            service = EmbeddingService()
            assert service.model == "text-embedding-3-small"
            assert service.client is None
    
    def test_embedding_service_with_model_override(self):
        """Test initialization with custom model"""
        with patch.dict(os.environ, {}, clear=True):
            service = EmbeddingService(model="text-embedding-3-large")
            assert service.model == "text-embedding-3-large"
    
    def test_embed_text_returns_none_without_client(self):
        """Test embed_text returns None when client is unavailable"""
        with patch.dict(os.environ, {}, clear=True):
            service = EmbeddingService()
            result = service.embed_text("test text")
            assert result is None
    
    def test_embed_text_handles_empty_text(self):
        """Test embed_text with empty text"""
        with patch.dict(os.environ, {}, clear=True):
            service = EmbeddingService()
            result = service.embed_text("")
            assert result is None
            
            result = service.embed_text("   ")
            assert result is None
    
    def test_embed_documents_returns_nones_without_client(self):
        """Test embed_documents returns list of Nones without client"""
        with patch.dict(os.environ, {}, clear=True):
            service = EmbeddingService()
            result = service.embed_documents(["doc1", "doc2", "doc3"])
            assert result == [None, None, None]
    
    @patch('src.vector_memory.embedding_service.OpenAI')
    def test_embed_text_with_mock_client(self, mock_openai_class):
        """Test embed_text with mocked OpenAI client"""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = EmbeddingService()
            result = service.embed_text("test text")
            
            assert result == [0.1, 0.2, 0.3]
            mock_client.embeddings.create.assert_called_once()
    
    @patch('src.vector_memory.embedding_service.OpenAI')
    def test_embed_documents_with_mock_client(self, mock_openai_class):
        """Test embed_documents with mocked OpenAI client"""
        mock_client = MagicMock()
        
        # Mock response for batch embedding
        mock_item1 = MagicMock()
        mock_item1.index = 0
        mock_item1.embedding = [0.1, 0.2]
        
        mock_item2 = MagicMock()
        mock_item2.index = 1
        mock_item2.embedding = [0.3, 0.4]
        
        mock_response = MagicMock()
        mock_response.data = [mock_item1, mock_item2]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = EmbeddingService()
            result = service.embed_documents(["doc1", "doc2"])
            
            assert len(result) == 2


class TestVectorStore:
    """Tests for VectorStore"""
    
    def test_vector_store_initialization_without_chromadb(self):
        """Test initialization when chromadb is unavailable"""
        with patch('src.vector_memory.vector_store.chromadb', None):
            store = VectorStore("test_collection")
            assert store.client is None
            assert store.collection is None
    
    def test_vector_store_with_persist_dir(self):
        """Test vector store initialization with persist directory"""
        with patch.dict(os.environ, {'CHROMADB_PERSIST_DIR': './test_dir'}):
            with patch('src.vector_memory.vector_store.chromadb') as mock_chroma:
                mock_client = MagicMock()
                mock_chroma.PersistentClient.return_value = mock_client
                mock_client.get_or_create_collection.return_value = MagicMock()
                
                store = VectorStore("test_collection")
                assert store.collection is not None
                mock_chroma.PersistentClient.assert_called()
    
    def test_add_documents_returns_early_without_collection(self):
        """Test add_documents when collection is unavailable"""
        store = VectorStore("test_collection")
        # Should not raise error
        store.add_documents(["doc1", "doc2"])
    
    def test_search_returns_empty_without_collection(self):
        """Test search when collection is unavailable"""
        store = VectorStore("test_collection")
        result = store.search("query")
        assert result == []
    
    def test_search_returns_empty_with_empty_query(self):
        """Test search with empty query"""
        store = VectorStore("test_collection")
        result = store.search("")
        assert result == []
        
        result = store.search("   ")
        assert result == []
    
    def test_delete_returns_early_without_collection(self):
        """Test delete when collection is unavailable"""
        store = VectorStore("test_collection")
        # Should not raise error
        store.delete(["id1", "id2"])
    
    def test_get_returns_empty_without_collection(self):
        """Test get when collection is unavailable"""
        store = VectorStore("test_collection")
        result = store.get(["id1", "id2"])
        assert result == []
    
    @patch('src.vector_memory.vector_store.EmbeddingService')
    @patch('src.vector_memory.vector_store.chromadb')
    def test_add_documents_with_mock_collection(self, mock_chroma, mock_embedding_service):
        """Test add_documents with mocked ChromaDB"""
        # Setup mocks
        mock_embedding_svc = MagicMock()
        mock_embedding_svc.embed_documents.return_value = [
            [0.1, 0.2],
            [0.3, 0.4]
        ]
        mock_embedding_service.return_value = mock_embedding_svc
        
        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.PersistentClient.return_value = mock_client
        
        store = VectorStore("test_collection", embedding_service=mock_embedding_svc)
        store.collection = mock_collection
        
        # Call add_documents
        docs = ["doc1", "doc2"]
        metas = [{"type": "a"}, {"type": "b"}]
        store.add_documents(docs, metadatas=metas)
        
        # Verify collection.add was called
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert 'ids' in call_args.kwargs
        assert 'documents' in call_args.kwargs
        assert 'embeddings' in call_args.kwargs
    
    @patch('src.vector_memory.vector_store.EmbeddingService')
    @patch('src.vector_memory.vector_store.chromadb')
    def test_search_with_mock_collection(self, mock_chroma, mock_embedding_service):
        """Test search with mocked ChromaDB"""
        mock_embedding_svc = MagicMock()
        mock_embedding_svc.embed_text.return_value = [0.1, 0.2]
        mock_embedding_service.return_value = mock_embedding_svc
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [['doc1', 'doc2']],
            'distances': [[0.1, 0.5]],
            'metadatas': [[{'type': 'a'}, {'type': 'b'}]],
            'ids': [['id1', 'id2']]
        }
        
        mock_client = MagicMock()
        mock_chroma.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        
        store = VectorStore("test_collection", embedding_service=mock_embedding_svc)
        store.collection = mock_collection
        
        results = store.search("test query", k=5)
        
        assert len(results) == 2
        assert results[0]['document'] == 'doc1'
        assert results[0]['similarity'] > 0
        assert results[1]['document'] == 'doc2'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
