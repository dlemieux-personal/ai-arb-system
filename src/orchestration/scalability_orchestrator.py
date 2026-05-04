"""
Scalability Agent Orchestrator
Coordinates end-to-end execution of the Scalability Agent task with integration to scoring pipeline
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from crewai import Crew, Agent, Task

from src.orchestration.task_specs import (
    ScalabilityTaskInput,
    ScalabilityTaskOutput,
    SCALABILITY_AGENT_TASK_SPEC,
)
from src.orchestration.task_output import TaskOutput, ScalabilityAgentTaskExecutor
from src.schemas.agent_outputs import ScalabilityAgentOutput
from src.agents.agent_factory import AgentFactory
from src.agents.definitions.scalability_agent import build_scalability_agent
from src.tools.retrieval_context import get_retrieval_context


@dataclass
class ScalabilityDimensionScore:
    """Scalability dimension score with metadata"""
    
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    bottleneck_count: int
    recommendation_count: int
    critical_bottlenecks: list[str]


class ScalabilityAgentOrchestrator:
    """
    Orchestrates end-to-end execution of the Scalability Agent task.
    
    This orchestrator:
    1. Validates task input
    2. Builds and executes the scalability review task
    3. Parses and validates the output
    4. Integrates results with the scoring pipeline
    5. Extracts critical bottlenecks for approval logic
    """
    
    def __init__(self, agent_factory: Optional[AgentFactory] = None):
        """
        Initialize the orchestrator
        
        Args:
            agent_factory: Optional AgentFactory instance
        """
        self.factory = agent_factory or AgentFactory()
        self.task_spec = SCALABILITY_AGENT_TASK_SPEC
        self.scalability_agent: Optional[Agent] = None
        self.scalability_task: Optional[Task] = None
    
    def build_task(self, architecture_description: str, submission_id: str, 
                   retrieval_context: Optional[str] = None) -> Task:
        """
        Build the scalability review task with retrieval context
        
        Args:
            architecture_description: Architecture to review
            submission_id: Submission identifier
            retrieval_context: Optional domain-specific context
            
        Returns:
            Configured Task instance
        """
        # Build scalability agent
        self.scalability_agent = build_scalability_agent()
        
        # Construct task description with format specification
        task_description = f"""Analyze the following architecture for scalability issues and performance bottlenecks:

{architecture_description}

IMPORTANT: You MUST provide your analysis in the exact structured markdown format specified below.

Required output format:
1. ## SCALABILITY BOTTLENECKS section with bullet points
2. ## SCALABILITY RECOMMENDATIONS section with bullet points  
3. ## SCALABILITY SCORE section with Overall Scalability Score and Confidence Level (both 0.XX format)
4. ## SUMMARY section with 2-4 sentences

Format specification:
- Each bottleneck/recommendation is a bullet point: `- **[Title]**: [Description]. Severity: [critical|high|medium|low]. Affected: [Component1, Component2]`
- Severity MUST be one of: critical, high, medium, low (exact case match required)
- Affected components is a comma-separated list of architecture components
- Score format: "Overall Scalability Score: 0.XX" (exactly 2 decimal places, 0.0-1.0 range)
- Confidence format: "Confidence Level: 0.XX" (exactly 2 decimal places, 0.0-1.0 range)

Example output structure:
## SCALABILITY BOTTLENECKS
- **Single database instance**: Database cannot scale horizontally. Severity: critical. Affected: Database, Backend

## SCALABILITY RECOMMENDATIONS
- **Implement sharding**: Partition data across multiple database instances. Severity: critical. Affected: Database, Storage

## SCALABILITY SCORE
Overall Scalability Score: 0.35
Confidence Level: 0.85

## SUMMARY
Critical scalability issues exist in the database layer that prevent horizontal scaling and will cause bottlenecks at moderate load.
"""
        
        if retrieval_context:
            task_description += f"\n\nRelevant Scalability Knowledge:\n{retrieval_context}"
        
        # Create task with expected output specification
        self.scalability_task = Task(
            description=task_description,
            agent=self.scalability_agent,
            expected_output="Structured scalability assessment in markdown format with bottlenecks, recommendations, score (0.0-1.0 with 2 decimals), confidence, and summary. MUST match the exact format specified above."
        )
        
        return self.scalability_task
    
    def execute_task(self, raw_output: str) -> TaskOutput[ScalabilityAgentOutput]:
        """
        Execute the parsing task on agent output
        
        Args:
            raw_output: Raw markdown output from scalability agent
            
        Returns:
            TaskOutput with parsed result
        """
        return ScalabilityAgentTaskExecutor.execute_and_parse(
            raw_output,
            agent_name="Scalability Agent"
        )
    
    def run_crew(self, architecture_description: str, submission_id: str,
                 retrieval_context: Optional[str] = None) -> ScalabilityTaskOutput:
        """
        Run the complete scalability review workflow with crew execution
        
        Args:
            architecture_description: Architecture to review
            submission_id: Submission identifier
            retrieval_context: Optional domain-specific context
            
        Returns:
            ScalabilityTaskOutput with validation and scoring
        """
        # Validate input
        task_input = {
            'architecture_description': architecture_description,
            'submission_id': submission_id,
            'retrieval_context': retrieval_context,
        }
        
        is_valid, error = self.task_spec.validate_input(task_input)
        if not is_valid:
            raise ValueError(f"Task input validation failed: {error}")
        
        # Build and execute scalability review task
        task = self.build_task(architecture_description, submission_id, retrieval_context)
        
        # Create crew with single scalability task
        if self.scalability_agent is None:
            raise RuntimeError("Scalability agent was not built. Call build_task() first.")
        
        crew = Crew(
            agents=[self.scalability_agent],
            tasks=[task],
            verbose=True
        )
        
        # Execute crew
        try:
            crew_output = crew.kickoff()
            raw_output = str(crew_output) if crew_output else ""
        except Exception as e:
            raw_output = f"Crew execution failed: {str(e)}"
        
        # Parse the output
        parsed_result = self.execute_task(raw_output)
        
        # Create output specification
        output = ScalabilityTaskOutput(
            agent_output=parsed_result.parsed_output or ScalabilityAgentOutput(
                bottlenecks=[],
                recommendations=[],
                scalability_score=0.50,
                confidence=0.0,
                summary="Parsing failed - using default score"
            ),
            raw_output=raw_output,
            parsing_successful=parsed_result.parsing_successful,
            parsing_error=parsed_result.parsing_error
        )
        
        # Validate output
        is_valid, error = self.task_spec.validate_output(output)
        if not is_valid:
            # Log error but don't fail - use fallback
            print(f"Output validation error: {error}")
        
        return output
    
    def get_dimension_score(self, task_output: ScalabilityTaskOutput) -> ScalabilityDimensionScore:
        """
        Extract dimension score metadata for integration with scoring pipeline
        
        Args:
            task_output: Task output with parsing results
            
        Returns:
            ScalabilityDimensionScore with extracted metadata
        """
        return ScalabilityDimensionScore(
            score=task_output.get_dimension_score(),
            confidence=task_output.agent_output.confidence if task_output.parsing_successful else 0.0,
            bottleneck_count=len(task_output.agent_output.bottlenecks) if task_output.parsing_successful else 0,
            recommendation_count=len(task_output.agent_output.recommendations) if task_output.parsing_successful else 0,
            critical_bottlenecks=task_output.get_critical_bottlenecks() if task_output.parsing_successful else []
        )


def create_scalability_orchestrator(agent_factory: Optional[AgentFactory] = None) -> ScalabilityAgentOrchestrator:
    """
    Factory function for creating a ScalabilityAgentOrchestrator
    
    Args:
        agent_factory: Optional AgentFactory instance
        
    Returns:
        Configured ScalabilityAgentOrchestrator instance
    """
    return ScalabilityAgentOrchestrator(agent_factory)
