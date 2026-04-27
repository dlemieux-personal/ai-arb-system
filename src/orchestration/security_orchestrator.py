"""
Security Agent Orchestrator
Coordinates end-to-end execution of the Security Agent task with integration to scoring pipeline
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from crewai import Crew, Agent, Task

from src.orchestration.task_specs import (
    SecurityTaskInput,
    SecurityTaskOutput,
    SECURITY_AGENT_TASK_SPEC,
)
from src.orchestration.task_output import TaskOutput, SecurityAgentTaskExecutor
from src.schemas.agent_outputs import SecurityAgentOutput
from src.agents.agent_factory import AgentFactory
from src.agents.definitions.security_agent import build_security_agent
from src.tools.retrieval_context import get_retrieval_context


@dataclass
class SecurityDimensionScore:
    """Security dimension score with metadata"""
    
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    critical_issues: list[str]
    findings_count: int
    recommendations_count: int


class SecurityAgentOrchestrator:
    """
    Orchestrates end-to-end execution of the Security Agent task.
    
    This orchestrator:
    1. Validates task input
    2. Builds and executes the security review task
    3. Parses and validates the output
    4. Integrates results with the scoring pipeline
    5. Extracts critical issues for approval logic
    """
    
    def __init__(self, agent_factory: Optional[AgentFactory] = None):
        """
        Initialize the orchestrator
        
        Args:
            agent_factory: Optional AgentFactory instance
        """
        self.factory = agent_factory or AgentFactory()
        self.task_spec = SECURITY_AGENT_TASK_SPEC
        self.security_agent: Optional[Agent] = None
        self.security_task: Optional[Task] = None
    
    def build_task(self, architecture_description: str, submission_id: str, 
                   retrieval_context: Optional[str] = None) -> Task:
        """
        Build the security review task with retrieval context
        
        Args:
            architecture_description: Architecture to review
            submission_id: Submission identifier
            retrieval_context: Optional domain-specific context
            
        Returns:
            Configured Task instance
        """
        # Build security agent
        self.security_agent = build_security_agent()
        
        # Construct task description with format specification
        task_description = f"""Review the following architecture for security risks and vulnerabilities:

{architecture_description}

IMPORTANT: You MUST provide your analysis in the exact structured markdown format specified below.

Required output format:
1. ## SECURITY FINDINGS section with bullet points
2. ## SECURITY RECOMMENDATIONS section with bullet points  
3. ## SECURITY SCORE section with Overall Security Score and Confidence Level (both 0.XX format)
4. ## SUMMARY section with 2-4 sentences

Format specification:
- Each finding/recommendation is a bullet point: `- **[Title]**: [Description]. Severity: [critical|high|medium|low]. Affected: [Component1, Component2]`
- Severity MUST be one of: critical, high, medium, low (exact case match required)
- Affected components is a comma-separated list of architecture components
- Score format: "Overall Security Score: 0.XX" (exactly 2 decimal places, 0.0-1.0 range)
- Confidence format: "Confidence Level: 0.XX" (exactly 2 decimal places, 0.0-1.0 range)

Example output structure:
## SECURITY FINDINGS
- **Missing encryption**: Database traffic is unencrypted. Severity: critical. Affected: Database, Network

## SECURITY RECOMMENDATIONS
- **Implement TLS**: Enable TLS for all database connections. Severity: critical. Affected: Database, Network

## SECURITY SCORE
Overall Security Score: 0.45
Confidence Level: 0.90

## SUMMARY
Critical security gaps exist in network encryption that require immediate remediation.
"""
        
        if retrieval_context:
            task_description += f"\n\nRelevant Security Knowledge:\n{retrieval_context}"
        
        # Create task with expected output specification
        self.security_task = Task(
            description=task_description,
            agent=self.security_agent,
            expected_output="Structured security assessment in markdown format with findings, recommendations, score (0.0-1.0 with 2 decimals), confidence, and summary. MUST match the exact format specified above."
        )
        
        return self.security_task
    
    def execute_task(self, raw_output: str) -> TaskOutput[SecurityAgentOutput]:
        """
        Execute the parsing task on agent output
        
        Args:
            raw_output: Raw markdown output from security agent
            
        Returns:
            TaskOutput with parsed result
        """
        return SecurityAgentTaskExecutor.execute_and_parse(
            raw_output,
            agent_name="Security Agent"
        )
    
    def run_crew(self, architecture_description: str, submission_id: str,
                 retrieval_context: Optional[str] = None) -> SecurityTaskOutput:
        """
        Run the complete security review workflow with crew execution
        
        Args:
            architecture_description: Architecture to review
            submission_id: Submission identifier
            retrieval_context: Optional domain-specific context
            
        Returns:
            SecurityTaskOutput with validation and scoring
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
        
        # Build and execute security review task
        task = self.build_task(architecture_description, submission_id, retrieval_context)
        
        # Create crew with single security task
        if self.security_agent is None:
            raise RuntimeError("Security agent was not built. Call build_task() first.")
        
        crew = Crew(
            agents=[self.security_agent],
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
        output = SecurityTaskOutput(
            agent_output=parsed_result.parsed_output or SecurityAgentOutput(
                findings=[],
                recommendations=[],
                security_score=0.50,
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
            print(f"Task output validation error: {error}")
        
        return output
    
    def extract_dimension_score(self, task_output: SecurityTaskOutput) -> SecurityDimensionScore:
        """
        Extract dimension score from task output for scoring pipeline integration
        
        Args:
            task_output: Executed task output
            
        Returns:
            SecurityDimensionScore with metrics for scoring model
        """
        score = task_output.get_dimension_score()
        confidence = task_output.agent_output.confidence if task_output.parsing_successful else 0.0
        
        return SecurityDimensionScore(
            score=score,
            confidence=confidence,
            critical_issues=task_output.get_critical_issues(),
            findings_count=len(task_output.agent_output.findings) if task_output.parsing_successful else 0,
            recommendations_count=len(task_output.agent_output.recommendations) if task_output.parsing_successful else 0,
        )


def create_security_orchestrator(agent_factory: Optional[AgentFactory] = None) -> SecurityAgentOrchestrator:
    """
    Factory function to create a security orchestrator
    
    Args:
        agent_factory: Optional AgentFactory instance
        
    Returns:
        Configured SecurityAgentOrchestrator
    """
    return SecurityAgentOrchestrator(agent_factory)
