# PR Summary: Reliability Agent - Schema Definition (PR 1/3)

**Status**: Draft / Planning  
**Date**: May 4, 2026  
**Type**: Feature - Agent Schema Implementation  
**Related**: Next agent in the AI-ARB multi-agent review pipeline after Scalability

---

## Overview

This PR begins the three-PR sequence for the **Reliability Agent** by defining the structured output schema, validation models, and parser requirements for reliability reviews. The focus is on establishing a machine-parseable contract for reliability findings, recommendations, and scoring that matches the existing Security and Scalability agent patterns.

**Key objective**: create a robust, type-safe schema and parser foundation for the Reliability Agent so the subsequent PRs can implement execution and pipeline integration cleanly.

---

## Motivation

Reliability is a core dimension of architecture review. The Reliability Agent must identify:

- fault tolerance gaps
- expected availability and recovery constraints
- operational resilience weaknesses
- dependency and service degradation risks

This PR ensures the Reliability Agent output is:

1. **Structured** for parser automation
2. **Validated** with clear score and severity rules
3. **Consistent** with the existing agent output style
4. **Extensible** for downstream orchestration and scoring logic

---

## Proposed Changes

### Files to Create

- `src/schemas/agent_outputs.py`
  - Add `ReliabilityAgentOutput` model
  - Add `ReliabilityFailureMode` model
  - Add `ReliabilityRecommendation` model
  - Add JSON schema examples and validation constraints

- `src/agents/system_prompts/reliability_prompt.md`
  - Define output format specification for the Reliability Agent
  - Include severity, impact, and recovery guidance

- `src/agents/output_parsers.py`
  - Add `ReliabilityAgentOutputParser`
  - Implement structured markdown parsing and section extraction

- `tests/test_reliability_agent_output.py`
  - Add model validation tests
  - Add parser tests for valid and invalid reliability markdown

### Files to Modify

- `src/orchestration/task_specs.py`
  - Register `RELIABILITY_AGENT_TASK_SPEC`
  - Add task input/output schema definitions for reliability

- `src/orchestration/task_output.py`
  - Add `ReliabilityAgentTaskExecutor` if needed for shared parsing logic later

---

## Design Notes

The Reliability Agent schema will follow the same structure used by Security and Scalability:

- `failures`: array of reliability issues with title, description, severity, and affected systems
- `recommendations`: array of reliability recommendations with the same schema
- `reliability_score`: numeric score between 0.0 and 1.0
- `confidence`: numeric confidence score between 0.0 and 1.0
- `summary`: short high-level assessment

Severity levels will align with existing agents: `critical`, `high`, `medium`, `low`.

---

## Test Plan

The new schema and parser tests will cover:

- valid reliability output parsing
- invalid severity values
- score and confidence range validation
- empty lists handling
- missing sections and malformed markdown detection

---

## Next Steps

After this PR is complete, the following PRs will be:

- **PR 2/3**: Reliability Agent task executor and CrewBuilder integration
- **PR 3/3**: Reliability orchestrator and ARB pipeline integration
