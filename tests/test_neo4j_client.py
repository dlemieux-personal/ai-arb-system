"""
Test Neo4j Client
Tests for Neo4j client node and relationship operations.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.knowledge_graph.neo4j_client import Neo4jClient
from src.knowledge_graph.graph_schema import GraphSchema


@pytest.fixture
def mock_driver():
    """Fixture providing a mock Neo4j driver."""
    return MagicMock()


@pytest.fixture
def client(mock_driver):
    """Fixture providing a Neo4jClient with mocked driver."""
    with patch('src.knowledge_graph.neo4j_client.GraphDatabase') as mock_gd:
        mock_gd.driver.return_value = mock_driver
        client = Neo4jClient("bolt://localhost:7687", "test", "test")
        client.driver = mock_driver
        return client


def test_create_node(client, mock_driver):
    """Test creating a node."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_record = {'n': {'id': 'test-123', 'name': 'TestNode', 'value': 42}}
    mock_session.run.return_value.single.return_value = mock_record
    
    result = client.create_node('TestLabel', {'name': 'TestNode', 'value': 42})
    
    assert result['id'] == 'test-123'
    assert result['name'] == 'TestNode'
    assert result['value'] == 42


def test_update_node(client, mock_driver):
    """Test updating a node."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_record = {'n': {'id': 'test-123', 'name': 'Updated'}}
    mock_session.run.return_value.single.return_value = mock_record
    
    result = client.update_node('TestLabel', 'test-123', {'name': 'Updated'})
    
    assert result['id'] == 'test-123'
    assert result['name'] == 'Updated'


def test_find_nodes(client, mock_driver):
    """Test finding nodes."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_records = [
        {'n': {'id': '1', 'name': 'Node1'}},
        {'n': {'id': '2', 'name': 'Node2'}}
    ]
    mock_session.run.return_value = iter(mock_records)
    
    results = client.find_nodes('TestLabel', criteria={'status': 'active'})
    
    assert len(results) == 2
    assert results[0]['id'] == '1'
    assert results[1]['id'] == '2'


def test_get_node(client, mock_driver):
    """Test getting a single node by id."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_record = {'n': {'id': 'test-123', 'name': 'TestNode'}}
    mock_session.run.return_value.single.return_value = mock_record
    
    result = client.get_node('TestLabel', 'test-123')
    
    assert result is not None
    assert result['id'] == 'test-123'
    assert result['name'] == 'TestNode'


def test_get_node_not_found(client, mock_driver):
    """Test getting a node that doesn't exist."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_session.run.return_value.single.return_value = None
    
    result = client.get_node('TestLabel', 'nonexistent')
    
    assert result is None


def test_create_relationship(client, mock_driver):
    """Test creating a relationship between nodes."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_session.run.return_value.single.return_value = {'r': {'created': True}}
    
    result = client.create_relationship(
        'Architecture', 'arch-1',
        'IMPLEMENTS',
        'Pattern', 'pat-1',
        validate_nodes=False  # Skip validation in unit tests
    )
    
    assert result is True


def test_create_architecture(client, mock_driver):
    """Test creating an Architecture node."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_record = {'n': {'id': 'arch-1', 'name': 'MyArch', 'description': 'Test architecture'}}
    mock_session.run.return_value.single.return_value = mock_record
    
    result = client.create_architecture('MyArch', 'Test architecture')
    
    assert result['name'] == 'MyArch'
    assert result['description'] == 'Test architecture'


def test_create_pattern(client, mock_driver):
    """Test creating a Pattern node."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    mock_record = {'n': {'id': 'pat-1', 'name': 'Microservices', 'category': 'Architecture'}}
    mock_session.run.return_value.single.return_value = mock_record
    
    result = client.create_pattern('Microservices', 'A pattern for distributed systems', 'Architecture')
    
    assert result['name'] == 'Microservices'
    assert result['category'] == 'Architecture'


def test_delete_node(client, mock_driver):
    """Test deleting a node."""
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=None)
    
    # Mock the counters from consume()
    mock_result = MagicMock()
    mock_result.counters.nodes_deleted = 1
    mock_session.run.return_value.consume.return_value = mock_result
    
    result = client.delete_node('TestLabel', 'test-123')
    
    assert result is True
