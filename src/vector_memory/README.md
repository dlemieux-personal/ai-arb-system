# Vector Memory Module

## Overview

The Vector Memory module provides semantic search and embeddings functionality for the AI-ARB system. It integrates with:

- **OpenAI Embeddings API** for generating vector embeddings
- **ChromaDB** for persistent vector storage and similarity search
- **Neo4j** knowledge graph for structured architectural data

Together, these components enable hybrid retrieval combining semantic similarity with graph relationships.

## Architecture

```
EmbeddingService
    ├── Uses OpenAI API to generate embeddings
    └── Supports batch embedding operations
    
VectorStore
    ├── Persists embeddings in ChromaDB
    ├── Performs similarity search
    └── Manages document collections
    
RetrievalService (Hybrid)
    ├── Vector similarity via VectorStore
    └── Graph queries via Neo4j for context
    
Vector Store Factory
    └── Creates and manages VectorStore instances
```

## Components

### 1. EmbeddingService

Generates vector embeddings for text using OpenAI's embedding models.

```python
from src.vector_memory.embedding_service import EmbeddingService

# Initialize
service = EmbeddingService(model="text-embedding-3-small")

# Single embedding
embedding = service.embed_text("Your text here")
# Returns: List[float] or None if service unavailable

# Batch embeddings
embeddings = service.embed_documents([
    "Document 1",
    "Document 2",
    "Document 3"
])
# Returns: List[Optional[List[float]]]
```

**Features:**
- Graceful degradation when OpenAI API key is missing
- Batch processing for multiple documents
- Empty text handling
- Error handling and logging

**Configuration:**
```bash
OPENAI_API_KEY=your-key-here
```

### 2. VectorStore

Manages vector storage and similarity search using ChromaDB.

```python
from src.vector_memory.vector_store import VectorStore

# Initialize
store = VectorStore(
    collection_name="architecture_reviews",
    persist_dir="./memory/embeddings_cache",
    embedding_service=embedding_service
)

# Add documents
store.add_documents(
    documents=["doc1", "doc2", "doc3"],
    metadatas=[
        {"type": "pattern", "domain": "architecture"},
        {"type": "review", "score": 0.85},
        {"type": "practice", "author": "team"}
    ]
)

# Search
results = store.search("query text", k=5)
# Returns: [
#   {
#     'id': 'uuid-123',
#     'document': 'matching text...',
#     'similarity': 0.89,
#     'metadata': {...}
#   },
#   ...
# ]

# Retrieve by ID
docs = store.get(['id1', 'id2'])

# Delete
store.delete(['id1', 'id2'])
```

**Features:**
- Persistent storage with ChromaDB
- Cosine similarity search (configurable)
- Metadata preservation
- Batch operations
- Automatic persist directory creation

**Configuration:**
```bash
CHROMADB_COLLECTION_NAME=architecture_reviews
CHROMADB_PERSIST_DIR=./memory/embeddings_cache
```

### 3. RetrievalService

High-level service providing hybrid retrieval combining vector similarity and graph queries.

```python
from src.vector_memory.retrieval_service import RetrievalService

# Initialize with both vector and graph stores
service = RetrievalService(
    vector_store=vector_store,
    neo4j_client=neo4j_client
)

# Retrieve similar previous reviews
reviews = service.retrieve_similar_reviews(
    submission="architecture description...",
    k=5
)

# Find relevant patterns
patterns = service.retrieve_relevant_patterns(
    keywords=["microservices", "scalability"],
    k=10
)

# Get best practices for a domain
practices = service.retrieve_best_practices(
    domain="architecture",
    k=10
)

# Find related architectures
related = service.retrieve_related_architectures(
    architecture_id="arch-123",
    k=5
)

# Get associated risks
risks = service.retrieve_architecture_risks(
    architecture_id="arch-123",
    k=10
)

# Generic semantic search
results = service.semantic_search("search query", k=10)
```

### 4. Vector Store Factory

Factory pattern for creating and managing VectorStore instances globally.

```python
from src.vector_memory.vector_store_factory import (
    create_vector_store,
    get_vector_store,
    close_vector_store
)

# Create new instance
store = create_vector_store(
    collection_name="my_collection",
    persist_dir="./my_persist",
    embedding_model="text-embedding-3-large"
)

# Get global instance (creates if needed)
store = get_vector_store()

# Cleanup
close_vector_store()
```

## Integration with ARB Pipeline

The vector memory module integrates with the ARB pipeline's retrieval stage:

```
Submission ──> Validate ──> Review ──> Score ──> [Retrieval] ──> Approve
                                                       ↓
                                        Vector Store + Neo4j
```

### In Agent Tasks

Agents can use retrieval for context:

```python
# In agent system prompts
retrieval = RetrievalService(vector_store, neo4j_client)

# Get similar past reviews for comparison
similar = retrieval.retrieve_similar_reviews(submission_text, k=3)

# Find relevant patterns and best practices
patterns = retrieval.retrieve_relevant_patterns(keywords, k=5)
```

## Hybrid Search Strategy

The RetrievalService combines two approaches:

### 1. Vector Similarity Search
- Query: "microservices architecture"
- Returns: Semantically similar documents
- Score: Cosine similarity (0-1)
- Use case: Conceptual matching

### 2. Graph Queries
- Query: Find architectures with domain="architecture"
- Returns: Structured relationships
- Context: Type, relationships, metadata
- Use case: Precise filtering

### 3. Combined Results
- Filter vector results by graph constraints
- Rank by similarity score
- Enrich with graph metadata
- Return k best results

## Usage Examples

### Basic Setup

```python
from src.vector_memory import (
    EmbeddingService,
    VectorStore,
    RetrievalService,
    get_vector_store
)
from src.knowledge_graph.graph_client_factory import get_neo4j_client

# Initialize components
embedding_service = EmbeddingService()
vector_store = get_vector_store()
neo4j_client = get_neo4j_client()

# Create retrieval service
retrieval = RetrievalService(
    vector_store=vector_store,
    neo4j_client=neo4j_client
)
```

### Loading Documents

```python
# Prepare documents with metadata
documents = [
    "Microservices architecture enables independent scaling",
    "Event-driven systems reduce coupling between services",
    "CQRS separates read and write models"
]

metadatas = [
    {"type": "pattern", "name": "Microservices", "domain": "architecture"},
    {"type": "pattern", "name": "Event-Driven", "domain": "architecture"},
    {"type": "pattern", "name": "CQRS", "domain": "data"}
]

# Add to vector store
vector_store.add_documents(documents, metadatas=metadatas)
```

### Searching

```python
# Semantic search
results = retrieval.semantic_search(
    "How should I design a scalable system?",
    k=5
)

for result in results:
    print(f"Document: {result['document']}")
    print(f"Similarity: {result['similarity']:.2f}")
    print(f"Metadata: {result['metadata']}")
```

## Error Handling

All components gracefully degrade when dependencies are unavailable:

```python
# If OPENAI_API_KEY is missing
embedding = service.embed_text("text")  # Returns None
embeddings = service.embed_documents(["d1", "d2"])  # Returns [None, None]

# If ChromaDB is not installed
store = VectorStore("collection")
store.search("query")  # Returns []

# If Neo4j is unavailable
retrieval = RetrievalService(vector_store=store, neo4j_client=None)
reviews = retrieval.retrieve_similar_reviews("text")  # Returns []
```

## Testing

### Run Unit Tests

```bash
# Test vector store and embedding service
pytest tests/test_vector_store.py -v

# Run all Neo4j tests including retrieval
pytest tests/test_neo4j_client.py tests/test_neo4j_tool.py -v
```

### Run Demonstrations

```bash
# Comprehensive demo of all components
python demo_chromadb.py

# Full system validation
python validate_system.py
```

## Performance Considerations

### Batch Embedding
For better performance, embed documents in batches:

```python
# Good: Single batch call
vectors = service.embed_documents(docs)  # 1 API call

# Avoid: Multiple individual calls
vectors = [service.embed_text(doc) for doc in docs]  # N API calls
```

### Collection Size
- Small (<10k documents): In-memory with ChromaDB Client()
- Large (>10k documents): Use PersistentClient with persist_dir

### Similarity Search
- Index built on first query (automatic)
- Subsequent queries are fast
- Update: Update embeddings then re-query

## Troubleshooting

### No Embeddings Generated

**Issue:** `embed_text()` returns None

**Solutions:**
1. Check OPENAI_API_KEY is set: `echo $env:OPENAI_API_KEY`
2. Verify API key is valid
3. Check OpenAI API status
4. Verify text is not empty

### ChromaDB Collection Empty

**Issue:** Search returns no results

**Solutions:**
1. Check documents were added: `store.get(['doc_id'])`
2. Verify embeddings were generated
3. Check query is semantically similar to documents
4. Review metadata filters

### Graph Query Returns No Results

**Issue:** `retrieve_related_architectures()` returns empty

**Solutions:**
1. Verify architecture exists in Neo4j
2. Check relationship types match schema
3. Run graph query directly: `neo4j_client.execute_query()`

## Environment Variables

```bash
# Embedding Model Configuration
OPENAI_API_KEY=sk-xxx...           # Required for embeddings
OPENAI_MODEL=gpt-4                 # Optional, default: text-embedding-3-small

# ChromaDB Configuration  
CHROMADB_COLLECTION_NAME=architecture_reviews
CHROMADB_PERSIST_DIR=./memory/embeddings_cache

# Neo4j Configuration (see knowledge_graph README)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

## Module Structure

```
src/vector_memory/
├── __init__.py                      # Module exports
├── embedding_service.py             # OpenAI embeddings
├── vector_store.py                  # ChromaDB storage
├── vector_store_factory.py          # Factory pattern
├── retrieval_service.py             # Hybrid retrieval
└── README.md                        # This file

tests/
├── test_vector_store.py             # Unit tests
└── (Neo4j tests also cover retrieval)

demos/
└── demo_chromadb.py                 # Comprehensive demo
```

## Related Documentation

- [Knowledge Graph Module](../knowledge_graph/README.md) - Neo4j integration
- [Orchestration Module](../orchestration/README.md) - ARB Pipeline
- [Agents Module](../agents/README.md) - Review agents
- [Tools Module](../tools/README.md) - Agent tools
