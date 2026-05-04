# PR: Security Agent Output Schema & Structured Markdown Format

## Overview

This PR implements the first piece of the agent specification framework: **structured output schemas and formatting for the Security Agent**. This enables reliable parsing of agent outputs and forms the foundation for consistent AI execution across all review dimensions.

## Problem Statement

Previously, the Security Agent output was entirely unstructured—agents produced free-form text with no guaranteed format. This made it impossible to reliably extract findings, scores, or recommendations for further processing.

This PR solves this by:
1. Defining **Pydantic models** for type-safe, validated output
2. Creating **JSON Schema** for documentation and LLM reference
3. Implementing a **structured markdown format** that's easy for LLMs to follow
4. Building a **parser** that converts markdown back into validated models
5. Providing **comprehensive tests** for all components

## What's Included

### 1. Pydantic Models (`src/schemas/agent_outputs.py`)

**Core Models:**
- `SecurityFinding` — One identified security issue with title, description, severity, affected components
- `SecurityRecommendation` — Actionable recommendation with same structure
- `SecurityAgentOutput` — Complete agent output with findings array, recommendations array, score, confidence, summary

**Key Features:**
- Type-safe validation with Pydantic v2
- Enum constraints on severity and score ranges
- Field descriptions for documentation
- Config examples for LLM reference

### 2. JSON Schema (`schemas/agent-output-security.json`)

Complete JSON Schema following draft-07 specification:
- Documented each field with descriptions and examples
- Specified valid enum values (critical/high/medium/low)
- Set array size limits (0-20 items)
- Added min/max length constraints for text fields
- Provides cross-reference to Pydantic models

**Purpose:** Serves as documentation for the agent prompt and enables validation

### 3. Updated Security Agent Prompt (`src/agents/system_prompts/security_prompt.md`)

**Structural Changes:**
- Replaced vague output format with explicit markdown template
- Added detailed format rules with examples
- Included parsing expectations for the agent
- Provided scoring guidance (0.0-1.0 scale with decision thresholds)

**Key Sections:**
```markdown
## SECURITY FINDINGS
- **[Title]**: [Description]. Severity: [critical|high|medium|low]. Affected: [Component1, Component2]

## SECURITY RECOMMENDATIONS  
- **[Title]**: [Description]. Severity: [critical|high|medium|low]. Affected: [Component1, Component2]

## SECURITY SCORE
Overall Security Score: 0.XX
Confidence Level: 0.XX

## SUMMARY
[2-4 sentences]
```

### 4. Markdown Parser (`src/agents/output_parsers.py`)

`SecurityAgentOutputParser` class:
- **`parse(markdown_output: str) → SecurityAgentOutput`** — Main entry point
- **`_extract_findings()`** — Parses SECURITY FINDINGS section
- **`_extract_recommendations()`** — Parses SECURITY RECOMMENDATIONS section
- **`_extract_scores()`** — Validates and extracts score/confidence with 2-decimal precision
- **`_extract_summary()`** — Gets SUMMARY text
- **Error handling:** Raises `SecurityMarkdownParseError` with clear messages if parsing fails

**Robustness:**
- Case-insensitive section matching
- Handles "None found" and "None - architecture is exemplary" cases
- Validates scores are in range 0.0-1.0 with 2 decimals
- Parses comma-separated component lists
- Regex-based extraction with clear error messages

### 5. Comprehensive Tests (`tests/test_security_agent_output.py`)

**20 tests covering:**

**Pydantic Models (9 tests):**
- Valid model creation
- Boundary conditions (0.0-1.0 scores, empty lists)
- Validation errors (invalid severity, missing required fields)
- All severity levels accepted

**Parser (11 tests):**
- Valid markdown parsing round-trip
- Findings extraction verification
- Recommendations extraction verification
- Empty findings/recommendations handling
- Missing section error detection
- Invalid score format detection
- Case-insensitive headers
- Multiple affected components
- Loss-less round-trip (output → markdown → re-parse)

## Design Decisions

### Structured Markdown vs JSON Output from Agent
**Decision:** Use structured markdown instead of demanding raw JSON from the agent

**Rationale:**
- LLMs often struggle to produce valid JSON with perfect formatting
- Markdown is more natural and flexible for language models
- Easier to include explanatory text alongside structured data
- Parser handles variations (whitespace, empty lines, etc.)
- Still achieves machine-readability via structured format

### 2 Decimal Precision for Scores
**Decision:** 0.75, 0.82 format (not 0-100 integers)

**Rationale:**
- Easy to interpret as percentages (75%, 82%)
- Matches weighted scoring threshold configuration already in `review_thresholds.yaml`
- Precise enough for decision logic, not too granular

### Severity as Priority in Recommendations
**Decision:** Same severity field for both findings and recommendations

**Rationale:**
- Finding severity = how bad is the issue?
- Recommendation severity = how urgent is fixing it?
- Using same field avoids duplication and confusion
- Aligns with approval logic already in `approval_logic.py`

## Usage Example

```python
from src.agents.output_parsers import SecurityAgentOutputParser

# Receive markdown from security agent
agent_output = """
## SECURITY FINDINGS

- **Missing TLS**: No encryption in transit. Severity: high. Affected: API Gateway, Services

## SECURITY RECOMMENDATIONS

- **Enable TLS 1.3**: Implement mTLS. Severity: high. Affected: API Gateway

## SECURITY SCORE

Overall Security Score: 0.72
Confidence Level: 0.89

## SUMMARY

Strong foundation with encryption gaps.
"""

# Parse into validated model
result = SecurityAgentOutputParser.parse(agent_output)

# Use structured data
print(f"Score: {result.security_score}")  # 0.72
print(f"Findings: {len(result.findings)}")  # 1
print(f"Finding severity: {result.findings[0].severity}")  # 'high'

# Validate it meets approval criteria
if result.security_score >= 0.70 and result.confidence >= 0.80:
    approve = True
```

## Next Steps

This PR is **self-contained** and can be merged independently. The next PR will implement:
- **Output parsing integration** into the SecurityAgent task definition
- **Scalability Agent** output schema and parsing
- **Parsing validation tests** in the orchestration pipeline

## Testing

✅ All 20 tests pass
- Pydantic model validation: ✓
- Parser accuracy: ✓  
- Round-trip conversion: ✓
- Error cases: ✓

```bash
pytest tests/test_security_agent_output.py -v
# 20 passed in 0.21s
```

## Files Changed

```
src/
  schemas/
    agent_outputs.py (NEW)
  agents/
    system_prompts/
      security_prompt.md (MODIFIED)
    output_parsers.py (NEW)
schemas/
  agent-output-security.json (NEW)
tests/
  test_security_agent_output.py (NEW)
```

## Validation Checklist

- [x] Pydantic models match JSON Schema
- [x] JSON Schema is valid draft-07
- [x] Security prompt clearly specifies format
- [x] Parser handles all valid formats
- [x] Parser gives clear errors on invalid input
- [x] Tests cover happy path and error cases
- [x] No breaking changes to existing code
- [x] All new code has type hints
- [x] Docstrings explain purpose and usage

## Breaking Changes

None. This PR only adds new modules and updates the security agent prompt. Existing code is unaffected.
