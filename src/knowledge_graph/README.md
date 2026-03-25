"""
Knowledge Graph Module README
Graph database integration for storing and querying architectural knowledge.
"""

# Neo4j Knowledge Graph Integration

This module provides comprehensive integration with Neo4j for managing an architecture knowledge graph.

## Components

### 1. Neo4j Client (`neo4j_client.py`)

The core client for interacting with the Neo4j database.

**Node Creation Methods:**
- `create_architecture(name, description, review_id)` - Create architecture nodes
- `create_pattern(name, description, category)` - Create architectural patterns
- `create_best_practice(title, description, domain)` - Create best practices
- `create_technology(name, type, description)` - Create technology nodes
- `create_risk(description, severity, mitigation)` - Create risk nodes
- `create_review(submission_id, status)` - Create review nodes
- `create_finding(type, severity, description)` - Create finding nodes

**Node Operations:**
- `create_node(label, properties)` - Generic node creation
- `update_node(label, node_id, properties)` - Update node properties
- `find_nodes(label, criteria)` - Find nodes by label and criteria
- `get_node(label, node_id)` - Retrieve a specific node by ID
- `delete_node(label, node_id)` - Delete a node

**Relationship Operations:**
- `create_relationship(start_label, start_id, rel_type, end_label, end_id, properties)`
- `find_relationship(start_label, start_id, rel_type, end_label, end_id)`

**Query Execution:**
- `execute_query(query, parameters)` - Execute raw Cypher queries

### 2. Graph Schema (`graph_schema.py`)

Defines the structure of the knowledge graph, including:
- Node labels: Architecture, Pattern, BestPractice, Technology, Risk, Review, Finding
- Relationship types: IMPLEMENTS, USES, MITIGATES, REFERENCES, SIMILAR_TO, etc.
- Property definitions for each node type

### 3. Graph Client Factory (`graph_client_factory.py`)

Utility functions for initializing the Neo4j client:
- `create_neo4j_client()` - Create a client from environment variables
- `get_neo4j_client()` - Get or create the global client instance
- `close_neo4j_client()` - Close the global client

### 4. Retrieval Service (`retrieval_service.py`)

High-level interface for knowledge retrieval:
- `retrieve_similar_reviews(submission, k)` - Find similar past reviews
- `retrieve_relevant_patterns(keywords)` - Search for architectural patterns
- `retrieve_best_practices(domain)` - Get best practices for a domain
- `retrieve_related_architectures(architecture_id)` - Find similar architectures
- `retrieve_architecture_risks(architecture_id)` - Get risks for an architecture

### 5. Query Tools (`src/tools/neo4j_tool.py`)

Crew AI tool for executing Cypher queries directly from agent tasks:
- `neo4j_query_tool(query, parameters)` - Execute parameterized Cypher queries

## Configuration

Set environment variables to connect to Neo4j:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Usage Examples

### Creating Nodes

```python
from src.knowledge_graph.neo4j_client import Neo4jClient

client = Neo4jClient(uri, user, password)

# Create nodes
arch = client.create_architecture(
    "Microservices Platform",
    "A distributed e-commerce system"
)

pattern = client.create_pattern(
    "API Gateway",
    "Central entry point for client requests",
    "Architectural"
)

bp = client.create_best_practice(
    "Service Independence",
    "Services should be independently deployable",
    "scalability"
)
```

### Creating Relationships

```python
client.create_relationship(
    "Architecture", arch['id'],
    "USES",
    "Pattern", pattern['id']
)

client.create_relationship(
    "Pattern", pattern['id'],
    "REFERENCES",
    "BestPractice", bp['id']
)
```

### Querying Nodes

```python
# Find all architectures
arches = client.find_nodes("Architecture")

# Find best practices for a domain
security_bps = client.find_nodes("BestPractice", {'domain': 'security'})

# Get a specific node
arch = client.get_node("Architecture", arch_id)
```

### Executing Cypher Queries

```python
query = """
MATCH (a:Architecture)-[:USES]->(p:Pattern)
RETURN a.name, p.name
"""
results = client.execute_query(query)
```

### Using Retrieval Service

```python
from src.vector_memory.retrieval_service import RetrievalService

service = RetrievalService(neo4j_client=client)

# Retrieve best practices
practices = service.retrieve_best_practices("security")

# Retrieve related architectures
related = service.retrieve_related_architectures(arch_id)
```

## Testing

Run unit tests for the Neo4j client:

```bash
pytest tests/test_neo4j_client.py -v
```

Run the interactive demo:

```bash
python demo_neo4j.py
```

## Node Labels and Properties

### Architecture
- `id` (string): Unique identifier
- `name` (string): Architecture name
- `description` (string): Architecture description
- `created_at` (datetime): Creation timestamp
- `review_id` (string): Associated review ID

### Pattern
- `id` (string): Unique identifier
- `name` (string): Pattern name
- `description` (string): Pattern description
- `category` (string): Pattern category

### BestPractice
- `id` (string): Unique identifier
- `title` (string): Practice title
- `description` (string): Practice description
- `domain` (string): Domain (e.g., security, scalability)

### Risk
- `id` (string): Unique identifier
- `description` (string): Risk description
- `severity` (string): Severity level
- `mitigation` (string): Mitigation strategy

### Review
- `id` (string): Unique identifier
- `submission_id` (string): Subject architecture ID
- `status` (string): Review status
- `date` (datetime): Review date

### Finding
- `id` (string): Unique identifier
- `type` (string): Finding type
- `severity` (string): Severity level
- `description` (string): Finding description

## Relationship Types

- `IMPLEMENTS` - Architecture implements a pattern
- `USES` - Architecture uses a technology or pattern
- `MITIGATES` - Risk mitigation relationship
- `REFERENCES` - Reference to a best practice
- `SIMILAR_TO` - Similar architectures
- `IDENTIFIED_IN` - Finding identified in architecture
- `CONTAINS` - Containment relationship
- `INDICATES` - Finding indicates a risk
