# AI Architecture Review Board (AI-ARB)

An intelligent, agent-based architecture review board system powered by Crew AI and LLMs. This system automates the review of architecture submissions across multiple dimensions including security, scalability, reliability, data architecture, cost optimization, and compliance.

## A Brief Note

This project is an attempt to utilize Agentic AI to resolve a common bottleneck within many organizations, which is the meeting-based Architecture Review Board (ARB). In many cases, ARBs only meet bi-weekly, and it cans sometimes take over a month for an architect to get on the ARB agenda, present their solution, hear feedback, apply it, and get approval to build. This solution allows architects to submit template-based submissions as PRs, which kick off the agentic process to give the submissions a standard first-pass review and scoring based on organizational best practices and requirements (see notes on the RAG process below), and then tag the ARB team in the PR to review the results. If there are questions, the ARB team can then reach out to the architect for confirmation, and any recommendations can be made in PR comments. Once the ARB team is satisfied, they can approve the PR, and the submission moves into the "Approved" section of the architecture source control.

When using this tool within an organization, some preparation work will be required to fit your organization's needs. The Neo4J and ChromaDB instances will need to be setup to establish baseline architecture patterns, established system architecture decisions, best practices, outcomes, and any other constraints or guardrails required to ensure the AI-ARB has the proper knowledge base to work from. In addition, prompts and settings will need to be customized within the src/agents/definitions and /src/agents/system_prompts folders to ensure the agent prompts match the requirements of your organization's architectural needs.

Data and Agent Definition guides are in progress, and will be added to this repo once complete.

## 🎯 Overview

AI-ARB processes architecture submissions through a multi-agent team that collaboratively reviews different aspects of proposed systems. Each agent is specialized in a specific domain and produces detailed findings that feed into a comprehensive scoring and recommendation system. The system then generates actionable improvement roadmaps with phased implementations, specific action items, and effort estimates.

### Why AI-ARB?

- **Consistent Reviews**: Eliminates subjective bias in architectural evaluations
- **Fast Feedback**: Generates comprehensive reviews in minutes, not weeks
- **Knowledge-Driven**: Leverages historical patterns and best practices via RAG
- **Async-Friendly**: Produces detailed PR comments for SME collaboration
- **Scalable**: Handles multiple concurrent reviews with consistent quality

## ✨ Key Features

- **Multi-Agent Architecture**: Specialized agents for security, scalability, reliability, data architecture, cost optimization, and compliance
- **Retrieval-Augmented Generation (RAG)**: Context-aware reviews using semantic search over architectural knowledge
- **Knowledge Graph Integration**: Neo4j-based storage of architecture patterns and best practices
- **Vector Memory System**: OpenAI embeddings (1536-dim) with ChromaDB for semantic retrieval
- **Intelligent Scoring**: 0.0-1.0 decimal scoring with configurable approval thresholds
- **Recommendation Engine**: Generates phased improvement roadmaps with action items and effort estimates
- **Comprehensive Reporting**: Detailed markdown reports and PR-ready comments
- **Fallback Resilience**: Graceful degradation when external services unavailable

## 🏗️ Architecture

```
Architecture Submission
        ↓
    Schema Validation
        ↓
    ARB Pipeline
        ├─→ Review Crew (6 agents)
        │   ├─→ Security Agent
        │   ├─→ Scalability Agent
        │   ├─→ Reliability Agent
        │   ├─→ Data Architecture Agent
        │   ├─→ Cost Optimization Agent
        │   ├─→ Compliance Agent
        │   └─→ Orchestrator Agent
        │
        ├─→ Recommendation Crew (6 agents)
        │   ├─→ Executive Summary Agent
        │   ├─→ Phased Roadmap Agent
        │   ├─→ Action Items Agent
        │   ├─→ Effort Estimation Agent
        │   ├─→ Success Criteria Agent
        │   └─→ Recommendation Orchestrator Agent
        │
        └─→ Results & Recommendations
            ├─→ Scoring & Approval Decision
            ├─→ Improvement Roadmap
            └─→ Action Items with Effort Estimates
```

## 📁 Project Structure

```
ai-arb-system/
├── config/                    # Configuration files (YAML)
├── schemas/                   # JSON schemas for submission validation
├── submissions/               # Submission management (incoming/validated/archived)
├── knowledge/                 # Best practices and architecture patterns
├── memory/                    # Vector indexes and embeddings cache
├── templates/                 # Architecture submission templates
├── src/                       # Core application code
│   ├── intake/               # Submission parsing and validation
│   ├── agents/               # Agent definitions and specializations
│   │   ├── definitions/      # Detailed agent prompts
│   │   └── system_prompts/   # System prompt templates
│   ├── orchestration/        # Pipeline and workflow management
│   │   ├── arb_pipeline.py   # Main review pipeline
│   │   ├── crew_builder.py   # Review crew construction
│   │   └── recommendation_crew_builder.py  # Recommendation crew construction
│   ├── models/               # Data models and schemas
│   ├── knowledge_graph/      # Neo4j integration
│   ├── vector_memory/        # Embeddings and retrieval
│   ├── scoring/              # Scoring and approval logic
│   ├── tools/                # Agent tools (search, query)
│   └── utils/                # Utilities and helpers
├── tests/                     # Comprehensive test suite
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata and config
├── .env.example              # Environment variables template
├── SOFTWARE_DESIGN_DOCUMENT.md  # Detailed design documentation
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Optional: Neo4j instance (for knowledge graph features)
- Optional: OpenAI API key (for embeddings and LLM)

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-arb-system.git
   cd ai-arb-system
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and service endpoints
   ```

### Running Your First Review

```python
from src.orchestration.arb_pipeline import ARBPipeline

# Initialize the pipeline
pipeline = ARBPipeline()

# Load an architecture submission
submission_file = "path/to/your/architecture.md"
submission = pipeline.load_submission(submission_file)

# Process the submission
result = pipeline.process_submission(submission)

# Generate recommendations
recommendations = pipeline.generate_recommendations(result)

# View results
print(result.overall_score)
print(result.approval_decision)
print(recommendations.executive_summary)
```

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all available options:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Neo4j Configuration (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here

# Vector Store Configuration
CHROMADB_COLLECTION_NAME=architecture_reviews
CHROMADB_PERSIST_DIR=./memory/embeddings_cache

# Review Configuration
APPROVAL_THRESHOLD=0.75
WARNING_THRESHOLD=0.50
```

### Configuration Files

- `config/arb_config.yaml` - Main system configuration and parameters
- `config/agent_config.yaml` - Agent-specific settings and personalities
- `config/scoring_weights.yaml` - Scoring weights for each review dimension
- `config/review_thresholds.yaml` - Approval decision thresholds

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_arb_pipeline.py -v

# Run tests matching a pattern
pytest tests/ -k "recommendation" -v
```

Current test suite: **27+ tests passing** covering:
- ARB pipeline end-to-end processing
- Context injection and retrieval
- Individual agent reasoning
- Scoring accuracy and thresholds
- Recommendation roadmap generation
- Tool functionality and integration

## 📊 Performance

- **Pipeline Processing Time**: ~30-60 seconds per submission
- **Context Retrieval**: <1 second per domain
- **Vector Search Latency**: ~100-500ms
- **Recommendation Generation**: ~60-120 seconds
- **Memory Usage**: ~200-300MB with loaded models
- **Test Coverage**: 27/27 core tests passing

## 📚 Documentation

- **[SOFTWARE_DESIGN_DOCUMENT.md](SOFTWARE_DESIGN_DOCUMENT.md)**: Comprehensive architecture and design decisions
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to contribute to the project
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**: Community guidelines
- **[SECURITY.md](SECURITY.md)**: Security policies and responsible disclosure

## 🛠️ Development

### Adding a Custom Review Agent

1. **Create agent definition** in `src/agents/definitions/`:
   ```python
   # src/agents/definitions/custom_agents.py
   class CustomReviewAgent:
       def __init__(self, ...):
           self.role = "Custom Reviewer"
           self.goal = "Review custom aspect"
   ```

2. **Create system prompt** in `src/agents/system_prompts/`:
   ```text
   You are a specialized architecture reviewer...
   ```

3. **Register in agent factory** (`src/agents/agent_factory.py`):
   ```python
   agents['custom'] = CustomReviewAgent(...)
   ```

### Code Style

This project uses:
- **Black** for code formatting (`black .`)
- **Pylint** for linting (`pylint src/`)
- **mypy** for type checking (`mypy src/`)

Run all checks:
```bash
black .
pylint src/
mypy src/
pytest tests/
```

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of Conduct
- How to report bugs
- How to suggest enhancements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🔒 Security

For security issues, please follow the responsible disclosure process in [SECURITY.md](SECURITY.md).

**Do not** open public issues for security vulnerabilities.

## 🙋 Support

- **Documentation**: See [SOFTWARE_DESIGN_DOCUMENT.md](SOFTWARE_DESIGN_DOCUMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-arb-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-arb-system/discussions)

## 📈 Roadmap

### Current Status (v0.1.0)
- ✅ Multi-agent architecture review system
- ✅ Knowledge graph and vector memory integration
- ✅ Intelligent recommendation engine
- ✅ Comprehensive testing and documentation

### Upcoming (v0.2.0)
- 🔄 Web interface for submissions and results
- 🔄 Report generation (PDF/HTML)
- 🔄 GitHub PR integration for automated comments
- 🔄 Batch processing for multiple submissions

### Future (v0.3+)
- 🔄 Machine learning integration for predictive scoring
- 🔄 Multi-modal input support (diagrams, code)
- 🔄 Collaborative human-AI review workflows
- 🔄 Industry benchmark comparisons
- 🔄 Custom organization-specific scoring models

## 🧠 Technology Stack

- **CrewAI**: Multi-agent orchestration and task management
- **Python 3.10+**: Primary development language
- **OpenAI API**: Embeddings and LLM access
- **Neo4j**: Knowledge graph storage
- **ChromaDB**: Vector database
- **Pydantic**: Data validation and serialization
- **PyYAML**: Configuration management
- **Pytest**: Test framework

---

**Status**: Production-ready with comprehensive testing and documentation  
**Last Updated**: March 25, 2026  
**Version**: 0.1.0
