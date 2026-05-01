"""
Task output wrapper and execution logic for agent results.
Handles parsing, validation, and error recovery for agent outputs.
"""

from dataclasses import dataclass
from typing import Optional, Any, Generic, TypeVar
from src.agents.output_parsers import (
    SecurityAgentOutputParser, SecurityMarkdownParseError,
    ScalabilityAgentOutputParser, ScalabilityMarkdownParseError
)
from src.schemas.agent_outputs import SecurityAgentOutput, ScalabilityAgentOutput

T = TypeVar('T')  # Generic type for parsed output


@dataclass
class TaskOutput(Generic[T]):
    """
    Wrapper for agent task output containing both raw and parsed results
    
    Type Parameters:
        T: The type of the parsed output (e.g., SecurityAgentOutput)
    """
    
    agent_name: str
    raw_output: str
    parsed_output: Optional[T] = None
    parsing_successful: bool = False
    parsing_error: Optional[str] = None
    parsing_attempts: int = 0
    
    def is_valid(self) -> bool:
        """Check if output was successfully parsed and validated"""
        return self.parsing_successful and self.parsed_output is not None
    
    def get_parsed_or_raise(self) -> T:
        """
        Get parsed output or raise an exception if parsing failed
        
        Returns:
            The parsed output object
            
        Raises:
            ValueError: If parsing was not successful
        """
        if not self.is_valid():
            raise ValueError(
                f"Output from {self.agent_name} could not be parsed: {self.parsing_error}"
            )
        return self.parsed_output


class SecurityAgentTaskExecutor:
    """
    Executes security agent tasks with output parsing and error handling
    """
    
    MAX_PARSE_RETRIES = 2
    
    @staticmethod
    def execute_and_parse(
        agent_output: str,
        agent_name: str = "Security Agent"
    ) -> TaskOutput[SecurityAgentOutput]:
        """
        Execute a security agent task and parse its output
        
        Args:
            agent_output: Raw markdown output from the agent
            agent_name: Name of the agent (for error messages)
            
        Returns:
            TaskOutput containing both raw and parsed results with error info
        """
        task_output = TaskOutput[SecurityAgentOutput](
            agent_name=agent_name,
            raw_output=agent_output
        )
        
        # Attempt parsing with retries
        for attempt in range(SecurityAgentTaskExecutor.MAX_PARSE_RETRIES + 1):
            task_output.parsing_attempts = attempt + 1
            
            try:
                parsed = SecurityAgentOutputParser.parse(agent_output)
                task_output.parsed_output = parsed
                task_output.parsing_successful = True
                task_output.parsing_error = None
                return task_output
            
            except SecurityMarkdownParseError as e:
                if attempt < SecurityAgentTaskExecutor.MAX_PARSE_RETRIES:
                    # Log and retry
                    print(f"Parsing attempt {attempt + 1} failed: {str(e)}")
                    print("Retrying...")
                else:
                    # Final attempt failed
                    task_output.parsing_successful = False
                    task_output.parsing_error = str(e)
            
            except Exception as e:
                # Unexpected error
                task_output.parsing_successful = False
                task_output.parsing_error = f"Unexpected error during parsing: {str(e)}"
                break
        
        return task_output
    
    @staticmethod
    def validate_output(parsed_output: SecurityAgentOutput) -> tuple[bool, str]:
        """
        Validate a parsed security agent output
        
        Args:
            parsed_output: The parsed SecurityAgentOutput object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []
        
        # Check score is in valid range
        if not (0.0 <= parsed_output.security_score <= 1.0):
            errors.append(f"Invalid security score: {parsed_output.security_score}")
        
        # Check confidence is in valid range
        if not (0.0 <= parsed_output.confidence <= 1.0):
            errors.append(f"Invalid confidence: {parsed_output.confidence}")
        
        # Check at least one finding or recommendation exists
        if not parsed_output.findings and not parsed_output.recommendations:
            errors.append("Output must contain at least findings or recommendations")
        
        # Check severity levels are valid
        valid_severities = {"critical", "high", "medium", "low"}
        for finding in parsed_output.findings:
            if finding.severity not in valid_severities:
                errors.append(f"Invalid finding severity: {finding.severity}")
        
        for rec in parsed_output.recommendations:
            if rec.severity not in valid_severities:
                errors.append(f"Invalid recommendation severity: {rec.severity}")
        
        is_valid = len(errors) == 0
        error_message = " | ".join(errors) if errors else ""
        
        return is_valid, error_message


class ScalabilityAgentTaskExecutor:
    """
    Executes scalability agent tasks with output parsing and error handling
    """
    
    MAX_PARSE_RETRIES = 2
    
    @staticmethod
    def execute_and_parse(
        agent_output: str,
        agent_name: str = "Scalability Agent"
    ) -> TaskOutput[ScalabilityAgentOutput]:
        """
        Execute a scalability agent task and parse its output
        
        Args:
            agent_output: Raw markdown output from the agent
            agent_name: Name of the agent (for error messages)
            
        Returns:
            TaskOutput containing both raw and parsed results with error info
        """
        task_output = TaskOutput[ScalabilityAgentOutput](
            agent_name=agent_name,
            raw_output=agent_output
        )
        
        # Attempt parsing with retries
        for attempt in range(ScalabilityAgentTaskExecutor.MAX_PARSE_RETRIES + 1):
            task_output.parsing_attempts = attempt + 1
            
            try:
                parsed = ScalabilityAgentOutputParser.parse(agent_output)
                task_output.parsed_output = parsed
                task_output.parsing_successful = True
                task_output.parsing_error = None
                return task_output
            
            except ScalabilityMarkdownParseError as e:
                if attempt < ScalabilityAgentTaskExecutor.MAX_PARSE_RETRIES:
                    # Log and retry
                    print(f"Parsing attempt {attempt + 1} failed: {str(e)}")
                    print("Retrying...")
                else:
                    # Final attempt failed
                    task_output.parsing_successful = False
                    task_output.parsing_error = str(e)
            
            except Exception as e:
                # Unexpected error
                task_output.parsing_successful = False
                task_output.parsing_error = f"Unexpected error during parsing: {str(e)}"
                break
        
        return task_output
    
    @staticmethod
    def validate_output(parsed_output: ScalabilityAgentOutput) -> tuple[bool, str]:
        """
        Validate a parsed scalability agent output
        
        Args:
            parsed_output: The parsed ScalabilityAgentOutput object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []
        
        # Check score is in valid range
        if not (0.0 <= parsed_output.scalability_score <= 1.0):
            errors.append(f"Invalid scalability score: {parsed_output.scalability_score}")
        
        # Check confidence is in valid range
        if not (0.0 <= parsed_output.confidence <= 1.0):
            errors.append(f"Invalid confidence: {parsed_output.confidence}")
        
        # Check at least one bottleneck or recommendation exists
        if not parsed_output.bottlenecks and not parsed_output.recommendations:
            errors.append("Output must contain at least bottlenecks or recommendations")
        
        # Check severity levels are valid
        valid_severities = {"critical", "high", "medium", "low"}
        for bottleneck in parsed_output.bottlenecks:
            if bottleneck.severity not in valid_severities:
                errors.append(f"Invalid bottleneck severity: {bottleneck.severity}")
        
        for rec in parsed_output.recommendations:
            if rec.severity not in valid_severities:
                errors.append(f"Invalid recommendation severity: {rec.severity}")
        
        is_valid = len(errors) == 0
        error_message = " | ".join(errors) if errors else ""
        
        return is_valid, error_message
