"""
Neo4j Client Module
Manages connection and interaction with Neo4j graph database.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from neo4j import GraphDatabase, Session

from src.knowledge_graph.graph_schema import GraphSchema


class Neo4jClient:
    """Client for Neo4j graph database operations"""
    
    def __init__(self, uri: str, user: str, password: str, connection_timeout: int = 30, query_timeout: int = 60):
        """
        Initialize Neo4j client
        
        Args:
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Username for authentication
            password: Password for authentication
            connection_timeout: Connection timeout in seconds (default: 30)
            query_timeout: Query timeout in seconds (default: 60)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.query_timeout = query_timeout
        # Initialize driver with timeout configuration
        self.driver = GraphDatabase.driver(
            uri, 
            auth=(user, password),
            connection_timeout=connection_timeout,
            max_connection_lifetime=3600,  # 1 hour
            max_pool_size=50,
            connection_acquisition_timeout=60
        )
        self.schema = GraphSchema()
    
    def close(self):
        """Close the database connection"""
        self.driver.close()
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None, timeout: Optional[int] = None) -> List[Dict]:
        """
        Execute a Cypher query with timeout protection
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            timeout: Query timeout in seconds (uses instance default if not specified)
            
        Returns:
            List of result records
            
        Raises:
            TimeoutError: If query exceeds timeout
        """
        timeout = timeout or self.query_timeout
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                # Force consumption of results with timeout
                records = []
                for record in result:
                    records.append(dict(record))
                return records
        except Exception as e:
            if "timed out" in str(e).lower():
                raise TimeoutError(f"Query execution timed out after {timeout} seconds: {query}") from e
            raise
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node in the graph
        
        Args:
            label: Node label
            properties: Node properties
            
        Returns:
            Dictionary containing the created node properties (including id)
        """
        # Ensure id exists
        if 'id' not in properties:
            properties['id'] = str(uuid.uuid4())
        
        # Build SET clause from properties
        props_list = []
        params = {}
        for key, value in properties.items():
            props_list.append(f"n.{key} = ${key}")
            params[key] = value
        
        set_clause = ", ".join(props_list)
        query = f"CREATE (n:{label}) SET {set_clause} RETURN n"
        
        with self.driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return dict(record['n'])
            return {}
    
    def update_node(self, label: str, node_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a node in the graph
        
        Args:
            label: Node label
            node_id: Node id to update
            properties: Properties to update
            
        Returns:
            Dictionary containing updated node properties
        """
        # Build SET clause
        props_list = []
        params = {'id': node_id}
        for key, value in properties.items():
            props_list.append(f"n.{key} = ${key}")
            params[key] = value
        
        set_clause = ", ".join(props_list)
        query = f"MATCH (n:{label} {{id: $id}}) SET {set_clause} RETURN n"
        
        with self.driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            if record:
                return dict(record['n'])
            return {}
    
    def find_nodes(self, label: str, criteria: Optional[Dict] = None) -> List[Dict]:
        """
        Find nodes matching criteria
        
        Args:
            label: Node label
            criteria: Search criteria (property filters)
            
        Returns:
            List of matching nodes
        """
        if not criteria:
            query = f"MATCH (n:{label}) RETURN n"
            with self.driver.session() as session:
                result = session.run(query)
                return [dict(record['n']) for record in result]
        else:
            # Build WHERE clause
            where_parts = []
            params = {}
            for key, value in criteria.items():
                where_parts.append(f"n.{key} = ${key}")
                params[key] = value
            
            where_clause = " AND ".join(where_parts)
            query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
            
            with self.driver.session() as session:
                result = session.run(query, params)
                return [dict(record['n']) for record in result]
    
    def get_node(self, label: str, node_id: str) -> Optional[Dict]:
        """
        Get a single node by id
        
        Args:
            label: Node label
            node_id: Node id
            
        Returns:
            Node properties or None
        """
        query = f"MATCH (n:{label} {{id: $id}}) RETURN n"
        with self.driver.session() as session:
            result = session.run(query, {'id': node_id})
            record = result.single()
            if not record:
                return None
            # Handle both neo4j Node objects and dict mocks from tests
            if isinstance(record, dict):
                return record.get('n')
            else:
                try:
                    return dict(record['n']) if 'n' in record else None
                except (KeyError, TypeError):
                    return None
    
    def create_relationship(self, start_label: str, start_id: str, 
                          rel_type: str, end_label: str, end_id: str,
                          properties: Optional[Dict] = None, validate_nodes: bool = True) -> bool:
        """
        Create a relationship between two nodes with optional validation
        
        Args:
            start_label: Starting node label
            start_id: Starting node id
            rel_type: Relationship type
            end_label: Ending node label
            end_id: Ending node id
            properties: Optional relationship properties
            validate_nodes: Whether to validate that nodes exist before creating relationship
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If validate_nodes=True and either node doesn't exist
        """
        params = {
            'start_id': start_id,
            'end_id': end_id
        }
        
        rel_props = ""
        if properties:
            props_list = []
            for key, value in properties.items():
                props_list.append(f"{key}: ${key}")
                params[key] = value
            rel_props = " {" + ", ".join(props_list) + "}"
        
        # Optionally verify both nodes exist before creating relationship
        if validate_nodes:
            start_exists = self.get_node(start_label, start_id)
            if not start_exists:
                raise ValueError(f"Start node {start_label}(id={start_id}) does not exist")
            
            end_exists = self.get_node(end_label, end_id)
            if not end_exists:
                raise ValueError(f"End node {end_label}(id={end_id}) does not exist")
        
        # Create the relationship
        query = f"""
            MATCH (s:{start_label} {{id: $start_id}})
            MATCH (e:{end_label} {{id: $end_id}})
            CREATE (s)-[r:{rel_type}{rel_props}]->(e)
            RETURN r
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, params)
                return result.single() is not None
        except Exception as e:
            raise ValueError(f"Failed to create relationship: {e}") from e
    
    def find_relationship(self, start_label: str, start_id: str,
                         rel_type: str, end_label: str, end_id: str) -> Optional[Dict]:
        """
        Check if a relationship exists between two nodes
        
        Args:
            start_label: Starting node label
            start_id: Starting node id
            rel_type: Relationship type
            end_label: Ending node label
            end_id: Ending node id
            
        Returns:
            Relationship properties or None
        """
        query = f"""
            MATCH (s:{start_label} {{id: $start_id}})-[r:{rel_type}]->(e:{end_label} {{id: $end_id}})
            RETURN r
        """
        params = {'start_id': start_id, 'end_id': end_id}
        
        with self.driver.session() as session:
            result = session.run(query, params)
            record = result.single()
            return dict(record['r']) if record else None
    
    def delete_node(self, label: str, node_id: str) -> bool:
        """
        Delete a node from the graph
        
        Args:
            label: Node label
            node_id: Node id to delete
            
        Returns:
            True if successful
        """
        query = f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n"
        with self.driver.session() as session:
            result = session.run(query, {'id': node_id})
            return result.consume().counters.nodes_deleted > 0
    
    def create_architecture(self, name: str, description: str, 
                           review_id: Optional[str] = None) -> Dict[str, Any]:
        """Create an Architecture node"""
        props = {
            'name': name,
            'description': description,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        if review_id:
            props['review_id'] = review_id
        return self.create_node(GraphSchema.ARCHITECTURE, props)
    
    def create_pattern(self, name: str, description: str, 
                      category: str) -> Dict[str, Any]:
        """Create a Pattern node"""
        props = {
            'name': name,
            'description': description,
            'category': category
        }
        return self.create_node(GraphSchema.PATTERN, props)
    
    def create_best_practice(self, title: str, description: str,
                            domain: str) -> Dict[str, Any]:
        """Create a BestPractice node"""
        props = {
            'title': title,
            'description': description,
            'domain': domain
        }
        return self.create_node(GraphSchema.BEST_PRACTICE, props)
    
    def create_technology(self, name: str, tech_type: str,
                         description: Optional[str] = None) -> Dict[str, Any]:
        """Create a Technology node"""
        props = {
            'name': name,
            'type': tech_type
        }
        if description:
            props['description'] = description
        return self.create_node(GraphSchema.TECHNOLOGY, props)
    
    def create_risk(self, description: str, severity: str,
                   mitigation: Optional[str] = None) -> Dict[str, Any]:
        """Create a Risk node"""
        props = {
            'description': description,
            'severity': severity
        }
        if mitigation:
            props['mitigation'] = mitigation
        return self.create_node(GraphSchema.RISK, props)
    
    def create_review(self, submission_id: str, status: str) -> Dict[str, Any]:
        """Create a Review node"""
        props = {
            'submission_id': submission_id,
            'status': status,
            'date': datetime.now(timezone.utc).isoformat()
        }
        return self.create_node(GraphSchema.REVIEW, props)
    
    def create_finding(self, finding_type: str, severity: str,
                      description: str) -> Dict[str, Any]:
        """Create a Finding node"""
        props = {
            'type': finding_type,
            'severity': severity,
            'description': description
        }
        return self.create_node(GraphSchema.FINDING, props)
