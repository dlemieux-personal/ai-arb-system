# AI Architecture Review Board (AI-ARB)

An intelligent, agent-based architecture review board system powered by Crew AI and LLMs. This project automates the review of architecture submissions across multiple dimensions including security, scalability, reliability, data architecture, cost optimization, and compliance.

## A Brief Note

AI-ARB is designed to reduce the time and coordination overhead of traditional Architecture Review Boards. Instead of months-long review cycles, architects can submit templated architecture proposals and receive a structured first-pass review, scoring, and recommendations from a multi-agent system.

This repository is built to be adapted for organizational needs. You will typically need:
- A knowledge base of patterns, decisions, and best practices
- A Neo4j instance for graph-based knowledge if you want advanced reasoning
- A vector store such as ChromaDB for semantic retrieval
- Custom prompt and agent configuration in `src/agents/definitions` and `src/agents/system_prompts`

## 🎯 Overview

AI-ARB processes architecture submissions through a multi-agent workflow. Each agent specializes in one domain, producing findings that feed into a comprehensive scoring and recommendation pipeline.

### Why AI-ARB?

- **Consistent reviews** across submissions
- **Faster feedback** than traditional meeting-based ARBs
- **Knowledge-driven results** via retrieval-augmented generation
- **PR-friendly output** for asynchronous collaboration
- **Extensible architecture** to add new review dimensions

## ✨ Key Features

- **Multi-agent review pipeline** for multiple architecture dimensions
- **Retrieval-Augmented Generation (RAG)** using semantic search over architectural knowledge
- **Knowledge graph support** via Neo4j
- **Vector memory storage** for embeddings and retrieval
- **Scoring and approval support** with configurable thresholds
- **Recommendation generation** for actionable improvement roadmaps
- **Graceful fallback behavior** when external services fail

## 🏗️ Architecture

```
Architecture Submission
        ↓
    Schema Validation
        ↓
    ARB Pipeline
        ├─→ Review Crew (domain-specific agents)
        │   ├─→ Security
        │   ├─→ Scalability
        │   ├─→ Reliability
        │   ├─→ Data Architecture
        │   ├─→ Cost Optimization
        │   └─→ Compliance
        │
        ├─→ Recommendation Crew
        │   ├─→ Executive Summary
        │   ├─→ Phased Roadmap
        │   ├─→ Action Items
        │   ├─→ Effort Estimation
        │   └─→ Recommendation Orchestrator
        │
        └─→ Results
            ├─→ Scoring
            ├─→ Approval Guidance
            └─→ PR-ready comments
```

## 📁 Project Structure

```
ai-arb-system/
├── config/                    # Configuration files
├── docs/                      # Documentation and PR summaries
│   └── pull_requests/         # PR summary documents
├── schemas/                   # JSON schemas for submission validation
├── submissions/               # Submission management
├── knowledge/                 # Best practices and architecture patterns
├── memory/                    # Vector indexes and embeddings cache
├── templates/                 # Architecture submission templates
├── src/                       # Core application code
│   ├── intake/                # Submission parsing and validation
│   ├── agents/                # Agent definitions and prompts
│   │   ├── definitions/       # Agent behaviors and builders
│   │   └── system_prompts/    # Agent prompt templates
│   ├── orchestration/         # Pipeline and workflow orchestration
│   ├── knowledge_graph/       # Neo4j integration
│   ├── vector_memory/         # Embeddings and retrieval
│   ├── scoring/               # Scoring and approval logic
│   ├── tools/                 # Agent tooling and connectors
│   └── utils/                 # Utilities and helpers
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata and tooling config
├── .env.example               # Environment variable template
├── README.md                  # This file
└── docs/                      # Documentation directory
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Optional: Neo4j instance for graph-backed knowledge storage
- Optional: OpenAI API key for embeddings and LLM support

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dlemieux-personal/ai-arb-system.git
   cd ai-arb-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   copy .env.example .env
   # On macOS/Linux: cp .env.example .env
   ```

5. Edit `.env` with your service credentials and endpoints.

### Running a Review

Use the orchestration pipeline in `src/orchestration/arb_pipeline.py` to process submissions.

```python
from src.orchestration.arb_pipeline import ARBPipeline

pipeline = ARBPipeline()
submission = pipeline.load_submission("path/to/architecture.md")
result = pipeline.process_submission(submission)

print(result.overall_score)
print(result.approval_decision)
```

## ⚙️ Configuration

### Environment Variables

See `.env.example` for available configuration options.

### Configuration Files

- `config/arb_config.yaml` - system and pipeline settings
- `config/agent_config.yaml` - agent-specific behavior and model settings
- `config/scoring_weights.yaml` - scoring weights for each review dimension
- `config/review_thresholds.yaml` - approval thresholds and review thresholds

## 🧪 Testing

Run the repository tests with pytest:

```bash
pytest tests/ -v
```

## 📚 Documentation

Project documentation lives under the `docs/` folder.

- `docs/CONTRIBUTING.md`
- `docs/FASTAPI_DESIGN_SPEC.md`
- `docs/MARKDOWN_SUBMISSION_GUIDE.md`
- `docs/SOFTWARE_DESIGN_DOCUMENT.md`
- `docs/pull_requests/` for PR summary documents

## 🛠️ Development

### Adding a new review agent

1. Add the agent definition in `src/agents/definitions/`.
2. Add the agent system prompt in `src/agents/system_prompts/`.
3. Register the new agent in `src/agents/agent_factory.py`.
4. Add tests under `tests/`.

### Project Conventions

- Use structured markdown for agent output
- Keep task schemas and parsers aligned
- Add regression tests for new review dimensions
- Keep documentation in `docs/`
