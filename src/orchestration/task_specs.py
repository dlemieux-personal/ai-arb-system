"""
Task Specifications for Agent Orchestration
Defines formal input/output contracts for agent tasks
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Type, List, TypeVar, Generic
from enum import Enum
from pydantic import BaseModel, Field


class TaskDomain(str, Enum):
    """Enumeration of review domains"""
    SECURITY = "security"
    SCALABILITY = "scalability"
    RELIABILITY = "reliability"
    DATA_ARCHITECTURE = "data_architecture"
    COST_OPTIMIZATION = "cost_optimization"
    COMPLIANCE = "compliance"


class TaskInputType(BaseModel):
    """Base input specification for any agent task"""
    
    architecture_description: str = Field(
        description="Description of the architecture to review"
    )
    submission_id: str = Field(
        description="Unique identifier for the submission"
    )
    retrieval_context: Optional[str] = Field(
        default=None,
        description="Domain-specific retrieval context from vector store/graph DB"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the submission"
    )


class TaskOutputType(BaseModel):
    """Base output specification for any agent task"""
    
    pass


@dataclass
class TaskSpecification:
    """Formal task specification with input/output contracts"""
    
    domain: TaskDomain
    task_name: str
    description: str
    input_schema: Type[TaskInputType]
    output_schema: Type[Any]  # Type-safe at runtime, flexible for all agent outputs
    expected_duration_seconds: int = 120
    max_retries: int = 2
    validation_rules: List[str] = field(default_factory=list)
    critical_failure_mode: str = "fallback_to_default_score"
    
    def validate_input(self, task_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate task input against schema
        
        Args:
            task_input: Input dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.input_schema(**task_input)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def validate_output(self, task_output: Any) -> tuple[bool, Optional[str]]:
        """
        Validate task output against schema
        
        Args:
            task_output: Output to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if isinstance(task_output, dict):
                self.output_schema(**task_output)
            else:
                # Already a model instance
                if not isinstance(task_output, self.output_schema):
                    return False, f"Output is not instance of {self.output_schema.__name__}"
            return True, None
        except Exception as e:
            return False, str(e)


# Security Agent Task Specification

class SecurityTaskInput(TaskInputType):
    """Input specification for Security review task"""
    pass  # Inherits all fields from TaskInputType


from src.schemas.agent_outputs import SecurityAgentOutput, ScalabilityAgentOutput, ReliabilityAgentOutput


class SecurityTaskOutput(BaseModel):
    """Output specification for Security review task"""
    
    agent_output: SecurityAgentOutput = Field(
        description="Parsed security agent output with findings, recommendations, and score"
    )
    raw_output: str = Field(
        description="Raw markdown output from the agent"
    )
    parsing_successful: bool = Field(
        description="Whether the output was successfully parsed"
    )
    parsing_error: Optional[str] = Field(
        default=None,
        description="Error message if parsing failed"
    )
    
    def get_dimension_score(self) -> float:
        """
        Extract dimension score for integration with scoring pipeline
        
        Returns:
            Security score (0.0-1.0)
        """
        if self.parsing_successful and self.agent_output:
            return self.agent_output.security_score
        # Fallback to neutral score if parsing failed
        return 0.50
    
    def get_critical_issues(self) -> List[str]:
        """
        Extract critical issues for approval logic
        
        Returns:
            List of critical finding titles
        """
        if self.parsing_successful and self.agent_output:
            return [
                f.title for f in self.agent_output.findings 
                if f.severity == "critical"
            ]
        return []


# Define the Security Agent Task Specification

SECURITY_AGENT_TASK_SPEC = TaskSpecification(
    domain=TaskDomain.SECURITY,
    task_name="Security Architecture Review",
    description="Comprehensive security review of the architecture identifying vulnerabilities, risks, and best practice violations",
    input_schema=SecurityTaskInput,
    output_schema=SecurityTaskOutput,
    expected_duration_seconds=120,
    max_retries=2,
    validation_rules=[
        "At least one finding or recommendation must be present",
        "Security score must be between 0.0 and 1.0",
        "Confidence level must be between 0.0 and 1.0",
        "All severity levels must be one of: critical, high, medium, low",
        "All affected components must be non-empty",
    ],
    critical_failure_mode="fallback_to_default_score"
)


# Scalability Agent Task Specification

class ScalabilityTaskInput(TaskInputType):
    """Input specification for Scalability review task"""
    pass  # Inherits all fields from TaskInputType


class ScalabilityTaskOutput(BaseModel):
    """Output specification for Scalability review task"""
    
    agent_output: ScalabilityAgentOutput = Field(
        description="Parsed scalability agent output with bottlenecks, recommendations, and score"
    )
    raw_output: str = Field(
        description="Raw markdown output from the agent"
    )
    parsing_successful: bool = Field(
        description="Whether the output was successfully parsed"
    )
    parsing_error: Optional[str] = Field(
        default=None,
        description="Error message if parsing failed"
    )
    
    def get_dimension_score(self) -> float:
        """
        Extract dimension score for integration with scoring pipeline
        
        Returns:
            Scalability score (0.0-1.0)
        """
        if self.parsing_successful and self.agent_output:
            return self.agent_output.scalability_score
        # Fallback to neutral score if parsing failed
        return 0.50
    
    def get_critical_bottlenecks(self) -> List[str]:
        """
        Extract critical bottlenecks for approval logic
        
        Returns:
            List of critical bottleneck titles
        """
        if self.parsing_successful and self.agent_output:
            return [
                b.title for b in self.agent_output.bottlenecks 
                if b.severity == "critical"
            ]
        return []


# Define the Scalability Agent Task Specification

SCALABILITY_AGENT_TASK_SPEC = TaskSpecification(
    domain=TaskDomain.SCALABILITY,
    task_name="Scalability Architecture Review",
    description="Comprehensive scalability review of the architecture identifying bottlenecks, performance limitations, and scaling barriers",
    input_schema=ScalabilityTaskInput,
    output_schema=ScalabilityTaskOutput,
    expected_duration_seconds=120,
    max_retries=2,
    validation_rules=[
        "At least one bottleneck or recommendation must be present",
        "Scalability score must be between 0.0 and 1.0",
        "Confidence level must be between 0.0 and 1.0",
        "All severity levels must be one of: critical, high, medium, low",
        "All affected components must be non-empty",
    ],
    critical_failure_mode="fallback_to_default_score"
)


class ReliabilityTaskInput(TaskInputType):
    """Input specification for Reliability review task"""
    pass  # Inherits all fields from TaskInputType


class ReliabilityTaskOutput(BaseModel):
    """Output specification for Reliability review task"""

    agent_output: ReliabilityAgentOutput = Field(
        description="Parsed reliability agent output with findings, failure modes, recommendations, and score"
    )
    raw_output: str = Field(
        description="Raw markdown output from the agent"
    )
    parsing_successful: bool = Field(
        description="Whether the output was successfully parsed"
    )
    parsing_error: Optional[str] = Field(
        default=None,
        description="Error message if parsing failed"
    )

    def get_dimension_score(self) -> float:
        """
        Extract dimension score for integration with scoring pipeline

        Returns:
            Reliability score (0.0-1.0)
        """
        if self.parsing_successful and self.agent_output:
            return self.agent_output.reliability_score
        return 0.50

    def get_critical_failure_modes(self) -> List[str]:
        """
        Extract critical failure mode titles for approval logic

        Returns:
            List of failure mode titles
        """
        if self.parsing_successful and self.agent_output:
            return [
                f.title for f in self.agent_output.failure_modes 
                if f.affected_components
            ]
        return []


RELIABILITY_AGENT_TASK_SPEC = TaskSpecification(
    domain=TaskDomain.RELIABILITY,
    task_name="Reliability Architecture Review",
    description="Comprehensive reliability review of the architecture identifying failure modes, resilience gaps, and recovery risks",
    input_schema=ReliabilityTaskInput,
    output_schema=ReliabilityTaskOutput,
    expected_duration_seconds=120,
    max_retries=2,
    validation_rules=[
        "At least one finding, failure mode, or recommendation must be present",
        "Reliability score must be between 0.0 and 1.0",
        "Confidence level must be between 0.0 and 1.0",
        "All severity levels must be one of: critical, high, medium, low",
        "All affected components must be non-empty",
    ],
    critical_failure_mode="fallback_to_default_score"
)


@dataclass
class TaskSpecs:
    """Registry of all task specifications"""
    
    specs: Dict[str, TaskSpecification] = field(default_factory=lambda: {
        "security": SECURITY_AGENT_TASK_SPEC,
        "scalability": SCALABILITY_AGENT_TASK_SPEC,
        "reliability": RELIABILITY_AGENT_TASK_SPEC
    })
    
    def get_spec(self, domain: str) -> Optional[TaskSpecification]:
        """Get specification for a domain"""
        return self.specs.get(domain)
    
    def get_all_specs(self) -> Dict[str, TaskSpecification]:
        """Get all specifications"""
        return self.specs.copy()
