#!/usr/bin/env python3
"""
AcmeTech Architectural Data Loader
Loads sample architectural evolution data for AcmeTech (computer hardware company).
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.vector_memory.vector_store_factory import get_vector_store
from src.knowledge_graph.graph_client_factory import get_neo4j_client
from src.vector_memory.embedding_service import EmbeddingService


def create_acmetech_architectures():
    """Create AcmeTech's architectural evolution submissions"""

    # Base submission template
    base_submission = {
        "submission_id": "",
        "team_name": "AcmeTech E-Commerce Team",
        "submission_date": "",
        "system_overview": {
            "title": "",
            "description": ""
        },
        "sections": {
            "architecture_diagram": "",
            "components": [],
            "data_flow": "",
            "scalability_considerations": "",
            "security_measures": "",
            "deployment_strategy": "",
            "monitoring_logging": "",
            "risks_concerns": ""
        }
    }

    # AcmeTech's architectural evolution
    architectures = [
        {
            "id": "acmetech-arch-001",
            "title": "Legacy Monolithic E-Commerce Platform (2018)",
            "date": "2018-06-15T10:00:00Z",
            "description": "Initial monolithic architecture built with Java/Spring, running on-premises with MySQL database. Single application server handling all e-commerce functions.",
            "architecture_type": "monolithic",
            "technologies": ["Java", "Spring Framework", "MySQL", "Apache Tomcat", "JSP"],
            "components": [
                "Web Frontend (JSP)",
                "Order Processing Service",
                "Inventory Management",
                "Shipping Calculator",
                "Payment Gateway Integration",
                "Customer Management"
            ],
            "data_flow": "All requests flow through single application server. Database is central bottleneck.",
            "scalability": "Vertical scaling only. Single points of failure throughout.",
            "security": "Basic authentication, no encryption in transit.",
            "deployment": "Manual deployment to on-premises servers.",
            "monitoring": "Basic log files, no centralized monitoring.",
            "risks": "Single point of failure, difficult to scale, slow deployment cycles.",
            "score": 0.35,
            "status": "rejected"
        },
        {
            "id": "acmetech-arch-002",
            "title": "Microservices Migration - Phase 1 (2020)",
            "date": "2020-03-20T14:30:00Z",
            "description": "First phase of microservices migration. Split monolithic application into separate services for order processing and inventory management.",
            "architecture_type": "microservices",
            "technologies": ["Java", "Spring Boot", "Spring Cloud", "MySQL", "Redis", "Docker"],
            "components": [
                "API Gateway (Spring Cloud Gateway)",
                "Order Service (Spring Boot)",
                "Inventory Service (Spring Boot)",
                "Legacy Web Frontend (JSP)",
                "Service Discovery (Eureka)",
                "Configuration Server"
            ],
            "data_flow": "API Gateway routes requests to appropriate microservices. Services communicate via REST APIs.",
            "scalability": "Services can be scaled independently. Still some coupling through shared database.",
            "security": "JWT tokens for service-to-service communication. Basic auth for users.",
            "deployment": "Docker containers deployed to on-premises Kubernetes cluster.",
            "monitoring": "Spring Boot Actuator, basic metrics collection.",
            "risks": "Database coupling between services, complex deployment, increased operational overhead.",
            "score": 0.62,
            "status": "conditional"
        },
        {
            "id": "acmetech-arch-003",
            "title": "Event-Driven Order Processing (2021)",
            "date": "2021-08-10T09:15:00Z",
            "description": "Introduced event-driven architecture for order processing using Apache Kafka. Implemented CQRS pattern for better scalability.",
            "architecture_type": "event-driven",
            "technologies": ["Java", "Spring Boot", "Apache Kafka", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes"],
            "components": [
                "API Gateway",
                "Order Command Service",
                "Order Query Service",
                "Inventory Service",
                "Shipping Service",
                "Payment Service",
                "Event Store (Kafka)",
                "Read Database (MongoDB)",
                "Write Database (PostgreSQL)"
            ],
            "data_flow": "Commands flow through Kafka to command services. Events published to query services for materialization.",
            "scalability": "Event-driven decoupling allows for better horizontal scaling. CQRS separates read/write workloads.",
            "security": "OAuth2 for API access, encrypted event streams, service mesh security.",
            "deployment": "Kubernetes with Helm charts, blue-green deployments.",
            "monitoring": "Prometheus metrics, ELK stack for logging, distributed tracing.",
            "risks": "Eventual consistency challenges, complex debugging, learning curve for event-driven patterns.",
            "score": 0.78,
            "status": "approved"
        },
        {
            "id": "acmetech-arch-004",
            "title": "Cloud-Native Migration (2022)",
            "date": "2022-11-05T16:45:00Z",
            "description": "Full migration to AWS cloud with serverless components. Implemented domain-driven design with bounded contexts.",
            "architecture_type": "cloud-native",
            "technologies": ["Java", "Spring Boot", "AWS Lambda", "API Gateway", "DynamoDB", "S3", "SNS", "SQS", "CloudFormation"],
            "components": [
                "API Gateway (AWS)",
                "Order Lambda Functions",
                "Inventory Lambda Functions",
                "Shipping Lambda Functions",
                "Payment Lambda Functions",
                "Event Bridge (AWS)",
                "DynamoDB Tables",
                "S3 Buckets",
                "CloudFront CDN"
            ],
            "data_flow": "Events flow through EventBridge. Lambda functions triggered by events. API Gateway handles external requests.",
            "scalability": "Serverless auto-scaling, pay-per-use model, global CDN distribution.",
            "security": "AWS IAM, VPC security groups, encrypted data at rest and in transit.",
            "deployment": "AWS CloudFormation, CI/CD pipelines with CodePipeline.",
            "monitoring": "CloudWatch metrics and logs, X-Ray tracing, AWS Config.",
            "risks": "Vendor lock-in, cold start latency, complex cost optimization.",
            "score": 0.82,
            "status": "approved"
        },
        {
            "id": "acmetech-arch-005",
            "title": "AI-Powered Supply Chain (2024)",
            "date": "2024-02-28T11:20:00Z",
            "description": "Modern distributed architecture with AI/ML components for demand forecasting and automated inventory optimization.",
            "architecture_type": "distributed-ai",
            "technologies": ["Kotlin", "Spring Boot", "Kubernetes", "PostgreSQL", "Redis", "Kafka", "TensorFlow", "AWS SageMaker", "GraphQL"],
            "components": [
                "GraphQL API Gateway",
                "Order Processing Service",
                "Inventory Optimization Service",
                "Demand Forecasting Service (ML)",
                "Supply Chain Orchestrator",
                "Shipping Optimization Service",
                "Customer Analytics Service",
                "Event Streaming Platform",
                "Multi-Region Database Cluster"
            ],
            "data_flow": "GraphQL federation for API composition. Event-driven communication between services. ML models integrated via prediction APIs.",
            "scalability": "Kubernetes HPA, multi-region deployment, AI model serving at scale.",
            "security": "Zero-trust architecture, service mesh (Istio), encrypted communications.",
            "deployment": "GitOps with ArgoCD, canary deployments, automated rollbacks.",
            "monitoring": "Observability platform with metrics, logs, traces, and AI-powered anomaly detection.",
            "risks": "AI model accuracy and bias, increased complexity, higher operational costs.",
            "score": 0.88,
            "status": "approved"
        }
    ]

    # Convert to submission format
    submissions = []
    for arch in architectures:
        submission = base_submission.copy()
        submission["submission_id"] = arch["id"]
        submission["submission_date"] = arch["date"]
        submission["system_overview"]["title"] = arch["title"]
        submission["system_overview"]["description"] = arch["description"]

        submission["sections"]["architecture_diagram"] = f"Architecture diagram for {arch['title']}"
        submission["sections"]["components"] = arch["components"]
        submission["sections"]["data_flow"] = arch["data_flow"]
        submission["sections"]["scalability_considerations"] = arch["scalability"]
        submission["sections"]["security_measures"] = arch["security"]
        submission["sections"]["deployment_strategy"] = arch["deployment"]
        submission["sections"]["monitoring_logging"] = arch["monitoring"]
        submission["sections"]["risks_concerns"] = arch["risks"]

        submissions.append(submission)

    return submissions, architectures


def create_architectural_patterns():
    """Create architectural patterns relevant to AcmeTech's evolution"""

    patterns = [
        {
            "id": "pattern-monolithic",
            "name": "Monolithic Architecture",
            "description": "Single unified application containing all functionality",
            "benefits": ["Simple development", "Easy testing", "Simple deployment"],
            "drawbacks": ["Tight coupling", "Scalability challenges", "Technology lock-in"],
            "when_to_use": "Small teams, simple applications, proof-of-concept projects",
            "domain": "architecture"
        },
        {
            "id": "pattern-microservices",
            "name": "Microservices Architecture",
            "description": "Application decomposed into small, independent services",
            "benefits": ["Independent scaling", "Technology diversity", "Fault isolation"],
            "drawbacks": ["Distributed complexity", "Operational overhead", "Data consistency"],
            "when_to_use": "Large applications, diverse scaling requirements, polyglot teams",
            "domain": "architecture"
        },
        {
            "id": "pattern-event-driven",
            "name": "Event-Driven Architecture",
            "description": "Components communicate through events and messages",
            "benefits": ["Loose coupling", "Asynchronous processing", "Scalability"],
            "drawbacks": ["Eventual consistency", "Debugging complexity", "Message ordering"],
            "when_to_use": "High-throughput systems, real-time processing, decoupled workflows",
            "domain": "architecture"
        },
        {
            "id": "pattern-cqrs",
            "name": "CQRS Pattern",
            "description": "Separate read and write models for better performance",
            "benefits": ["Optimized reads/writes", "Independent scaling", "Complex queries"],
            "drawbacks": ["Increased complexity", "Eventual consistency", "Dual models"],
            "when_to_use": "High-read systems, complex queries, performance-critical applications",
            "domain": "architecture"
        },
        {
            "id": "pattern-serverless",
            "name": "Serverless Computing",
            "description": "Run code without managing servers",
            "benefits": ["Auto-scaling", "Pay-per-use", "Reduced operational overhead"],
            "drawbacks": ["Cold starts", "Vendor lock-in", "Limited customization"],
            "when_to_use": "Variable workloads, event-driven processing, cost optimization",
            "domain": "architecture"
        },
        {
            "id": "pattern-api-gateway",
            "name": "API Gateway Pattern",
            "description": "Single entry point for client requests to microservices",
            "benefits": ["Centralized access", "Cross-cutting concerns", "Protocol translation"],
            "drawbacks": ["Single point of failure", "Increased latency", "Complexity"],
            "when_to_use": "Microservices architectures, multiple client types, API management",
            "domain": "architecture"
        }
    ]

    return patterns


def create_best_practices():
    """Create best practices for e-commerce architectures"""

    practices = [
        {
            "id": "practice-inventory-consistency",
            "name": "Inventory Consistency in Distributed Systems",
            "description": "Ensure inventory accuracy across distributed services using event sourcing and sagas",
            "domain": "data_architecture",
            "category": "consistency"
        },
        {
            "id": "practice-order-processing",
            "name": "Idempotent Order Processing",
            "description": "Design order processing to handle duplicate requests safely",
            "domain": "reliability",
            "category": "fault_tolerance"
        },
        {
            "id": "practice-payment-security",
            "name": "PCI DSS Compliance in Microservices",
            "description": "Isolate payment processing in dedicated services with strict security controls",
            "domain": "security",
            "category": "compliance"
        },
        {
            "id": "practice-scaling-ecommerce",
            "name": "Auto-scaling E-commerce During Peak Traffic",
            "description": "Implement predictive scaling based on historical data and marketing campaigns",
            "domain": "scalability",
            "category": "performance"
        },
        {
            "id": "practice-cost-optimization",
            "name": "Cost Optimization in Cloud E-commerce",
            "description": "Use spot instances, reserved capacity, and serverless for cost-effective scaling",
            "domain": "cost_optimization",
            "category": "efficiency"
        }
    ]

    return practices


def load_data_into_system():
    """Load all AcmeTech data into the system"""

    print("\n" + "="*70)
    print("ACMETECH ARCHITECTURAL DATA LOADER")
    print("="*70)

    # Initialize components
    embedding_service = EmbeddingService()
    vector_store = get_vector_store()
    neo4j_client = get_neo4j_client()

    print(f"\n✓ Components initialized:")
    print(f"  Embedding service: {embedding_service.client is not None}")
    print(f"  Vector store: {vector_store.collection is not None}")
    print(f"  Neo4j client: {neo4j_client is not None}")

    # Create data
    submissions, architectures = create_acmetech_architectures()
    patterns = create_architectural_patterns()
    practices = create_best_practices()

    print(f"\n✓ Data prepared:")
    print(f"  Architecture submissions: {len(submissions)}")
    print(f"  Architectural patterns: {len(patterns)}")
    print(f"  Best practices: {len(practices)}")

    # Load architectures into vector store
    print(f"\n--- Loading Architecture Submissions ---")

    arch_documents = []
    arch_metadatas = []

    for arch in architectures:
        # Create document for vector search
        doc = f"""
        Title: {arch['title']}
        Description: {arch['description']}
        Architecture Type: {arch['architecture_type']}
        Technologies: {', '.join(arch['technologies'])}
        Components: {', '.join(arch['components'])}
        Data Flow: {arch['data_flow']}
        Scalability: {arch['scalability']}
        Security: {arch['security']}
        Deployment: {arch['deployment']}
        Monitoring: {arch['monitoring']}
        Risks: {arch['risks']}
        Overall Score: {arch['score']}
        Status: {arch['status']}
        """

        metadata = {
            "type": "architecture",
            "id": arch["id"],
            "title": arch["title"],
            "architecture_type": arch["architecture_type"],
            "technologies": ", ".join(arch["technologies"]),  # Convert list to string
            "score": arch["score"],
            "status": arch["status"],
            "date": arch["date"]
        }

        arch_documents.append(doc.strip())
        arch_metadatas.append(metadata)

    # Add to vector store
    vector_store.add_documents(arch_documents, metadatas=arch_metadatas)
    print(f"✓ Added {len(arch_documents)} architecture submissions to vector store")

    # Load patterns into vector store
    print(f"\n--- Loading Architectural Patterns ---")

    pattern_documents = []
    pattern_metadatas = []

    for pattern in patterns:
        doc = f"""
        Pattern: {pattern['name']}
        Description: {pattern['description']}
        Benefits: {', '.join(pattern['benefits'])}
        Drawbacks: {', '.join(pattern['drawbacks'])}
        When to Use: {pattern['when_to_use']}
        Domain: {pattern['domain']}
        """

        metadata = {
            "type": "pattern",
            "id": pattern["id"],
            "name": pattern["name"],
            "domain": pattern["domain"]
        }

        pattern_documents.append(doc.strip())
        pattern_metadatas.append(metadata)

    vector_store.add_documents(pattern_documents, metadatas=pattern_metadatas)
    print(f"✓ Added {len(pattern_documents)} architectural patterns to vector store")

    # Load best practices into vector store
    print(f"\n--- Loading Best Practices ---")

    practice_documents = []
    practice_metadatas = []

    for practice in practices:
        doc = f"""
        Practice: {practice['name']}
        Description: {practice['description']}
        Domain: {practice['domain']}
        Category: {practice['category']}
        """

        metadata = {
            "type": "practice",
            "id": practice["id"],
            "name": practice["name"],
            "domain": practice["domain"],
            "category": practice["category"]
        }

        practice_documents.append(doc.strip())
        practice_metadatas.append(metadata)

    vector_store.add_documents(practice_documents, metadatas=practice_metadatas)
    print(f"✓ Added {len(practice_documents)} best practices to vector store")

    # Load into Neo4j knowledge graph
    if neo4j_client:
        print(f"\n--- Loading Data into Knowledge Graph ---")

        # Create architectures and store their actual IDs
        arch_id_map = {}  # Maps display IDs to actual database IDs
        for arch in architectures:
            try:
                node = neo4j_client.create_architecture(
                    name=arch["title"],
                    description=arch["description"]
                )
                actual_id = node.get('id')
                arch_id_map[arch["id"]] = actual_id
                print(f"  ✓ Created architecture: {arch['title']} (id: {actual_id[:8]}...)")
            except Exception as e:
                print(f"  ⚠ Failed to create architecture {arch['title']}: {e}")

        # Create patterns and store their actual IDs
        pattern_id_map = {}
        for pattern in patterns:
            try:
                node = neo4j_client.create_pattern(
                    name=pattern["name"],
                    description=pattern["description"],
                    category=pattern["domain"]
                )
                actual_id = node.get('id')
                pattern_id_map[pattern["id"]] = actual_id
                print(f"  ✓ Created pattern: {pattern['name']} (id: {actual_id[:8]}...)")
            except Exception as e:
                print(f"  ⚠ Failed to create pattern {pattern['name']}: {e}")

        # Create best practices and store their actual IDs
        practice_id_map = {}
        for practice in practices:
            try:
                node = neo4j_client.create_best_practice(
                    title=practice["name"],
                    description=practice["description"],
                    domain=practice["domain"]
                )
                actual_id = node.get('id')
                practice_id_map[practice["id"]] = actual_id
                print(f"  ✓ Created best practice: {practice['name']} (id: {actual_id[:8]}...)")
            except Exception as e:
                print(f"  ⚠ Failed to create best practice {practice['name']}: {e}")

        # Create relationships between architectures and patterns
        print(f"\n--- Creating Architecture-Pattern Relationships ---")

        # Map architectures to relevant patterns
        arch_pattern_relationships = [
            ("acmetech-arch-001", "pattern-monolithic"),
            ("acmetech-arch-002", "pattern-microservices"),
            ("acmetech-arch-002", "pattern-api-gateway"),
            ("acmetech-arch-003", "pattern-event-driven"),
            ("acmetech-arch-003", "pattern-cqrs"),
            ("acmetech-arch-004", "pattern-serverless"),
            ("acmetech-arch-004", "pattern-api-gateway"),
            ("acmetech-arch-005", "pattern-microservices"),
            ("acmetech-arch-005", "pattern-event-driven"),
        ]

        created_relationships = 0
        skipped_relationships = 0
        
        for arch_id, pattern_id in arch_pattern_relationships:
            try:
                # Look up actual database IDs
                actual_arch_id = arch_id_map.get(arch_id)
                actual_pattern_id = pattern_id_map.get(pattern_id)
                
                if not actual_arch_id:
                    print(f"  ⚠ Architecture {arch_id} not found in database, skipping relationship")
                    skipped_relationships += 1
                    continue
                
                if not actual_pattern_id:
                    print(f"  ⚠ Pattern {pattern_id} not found in database, skipping relationship")
                    skipped_relationships += 1
                    continue
                
                success = neo4j_client.create_relationship(
                    start_label="Architecture",
                    start_id=actual_arch_id,
                    rel_type="USES_PATTERN",
                    end_label="Pattern",
                    end_id=actual_pattern_id,
                    validate_nodes=True  # Validate nodes exist to prevent hanging queries
                )
                
                if success:
                    print(f"  ✓ Created relationship: {arch_id} -> {pattern_id}")
                    created_relationships += 1
                else:
                    print(f"  ✗ Failed to create relationship: {arch_id} -> {pattern_id}")
                    skipped_relationships += 1
                    
            except ValueError as e:
                # Node doesn't exist
                print(f"  ✗ Cannot create relationship {arch_id}->{pattern_id}: {e}")
                skipped_relationships += 1
            except Exception as e:
                print(f"  ⚠ Failed to create relationship {arch_id}->{pattern_id}: {e}")
                skipped_relationships += 1
        
        print(f"\nRelationship creation summary: {created_relationships} created, {skipped_relationships} skipped")

    # Save submission files
    print(f"\n--- Saving Submission Files ---")

    submissions_dir = Path("./submissions/acmetech")
    submissions_dir.mkdir(parents=True, exist_ok=True)

    for submission in submissions:
        filename = f"{submission['submission_id']}.json"
        filepath = submissions_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(submission, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved submission: {filename}")

    print(f"\n" + "="*70)
    print("✓ ACMETECH DATA LOADING COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"  • {len(architectures)} architecture submissions loaded")
    print(f"  • {len(patterns)} architectural patterns loaded")
    print(f"  • {len(practices)} best practices loaded")
    print(f"  • Vector store populated with {len(arch_documents) + len(pattern_documents) + len(practice_documents)} documents")
    print(f"  • Knowledge graph populated with nodes and relationships")
    print(f"  • Submission files saved to: {submissions_dir}")
    print(f"\n🚀 Ready for ARB pipeline processing!")


if __name__ == "__main__":
    try:
        load_data_into_system()
    except Exception as e:
        print(f"\n✗ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
