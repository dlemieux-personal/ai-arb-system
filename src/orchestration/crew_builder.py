"""
Crew Builder Module
Creates and configures the Crew AI orchestration for architecture reviews.
"""

from crewai import Crew, Agent, Task, Process
from src.agents.agent_factory import AgentFactory
from src.tools.retrieval_context import get_retrieval_context
from typing import Dict, Any, List, Optional
from pathlib import Path


class CrewBuilder:
    """Builder for creating the architecture review crew"""
    
    def __init__(self, factory: Optional[AgentFactory] = None):
        """
        Initialize the crew builder
        
        Args:
            factory: Optional AgentFactory instance. If not provided, creates a new one.
        """
        self.factory = factory or AgentFactory()
        self.agents = {}
        self.tasks = {}
    
    def build_agents(self) -> Dict[str, Agent]:
        """
        Build all review agents
        
        Returns:
            Dictionary of configured agents
        """
        self.agents = self.factory.create_all_review_agents()
        return self.agents
    
    def build_review_crew(self, description: str) -> Crew:
        """
        Build the complete architecture review crew with agents and tasks
        
        Args:
            description: Description of the architecture to review
            
        Returns:
            Configured Crew instance
        """
        # Ensure agents are built
        if not self.agents:
            self.build_agents()
        
        # Build tasks for each agent
        tasks = self._create_review_tasks(description)
        
        # Create the crew with agents and tasks
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            process=Process.sequential  # Review agents work sequentially
        )
        
        return crew
    
    def _create_review_tasks(self, description: str) -> List[Task]:
        """
        Create review tasks for each agent with retrieval context
        
        Args:
            description: Description of the architecture to review
            
        Returns:
            List of Task instances enhanced with retrieval context
        """
        # Initialize retrieval context manager with the submission
        try:
            context_manager = get_retrieval_context(description)
        except Exception as e:
            print(f"Warning: Could not initialize retrieval context: {e}")
            context_manager = None
        
        tasks = []
        
        # Security review task
        if 'security' in self.agents:
            security_context = ""
            if context_manager:
                try:
                    security_context = context_manager.get_context_for_domain('security')
                except Exception as e:
                    print(f"Warning: Could not retrieve security context: {e}")
            
            task_description = f"Review the following architecture for security risks and vulnerabilities:\n{description}"
            if security_context:
                task_description += f"\n\nRelevant Security Knowledge:\n{security_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['security'],
                expected_output="Security evaluation with identified risks and recommendations"
            ))
        
        # Scalability review task
        if 'scalability' in self.agents:
            scalability_context = ""
            if context_manager:
                try:
                    scalability_context = context_manager.get_context_for_domain('scalability')
                except Exception as e:
                    print(f"Warning: Could not retrieve scalability context: {e}")
            
            task_description = f"Review the following architecture for scalability issues and bottlenecks:\n{description}"
            if scalability_context:
                task_description += f"\n\nRelevant Scalability Knowledge:\n{scalability_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['scalability'],
                expected_output="Scalability evaluation with identified bottlenecks and recommendations"
            ))
        
        # Reliability review task
        if 'reliability' in self.agents:
            reliability_context = ""
            if context_manager:
                try:
                    reliability_context = context_manager.get_context_for_domain('reliability')
                except Exception as e:
                    print(f"Warning: Could not retrieve reliability context: {e}")
            
            task_description = f"Review the following architecture for reliability concerns and failure modes:\n{description}"
            if reliability_context:
                task_description += f"\n\nRelevant Reliability Knowledge:\n{reliability_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['reliability'],
                expected_output="Reliability evaluation with identified failure modes and recommendations"
            ))
        
        # Data architecture review task
        if 'data_architecture' in self.agents:
            data_context = ""
            if context_manager:
                try:
                    data_context = context_manager.get_context_for_domain('data')
                except Exception as e:
                    print(f"Warning: Could not retrieve data context: {e}")
            
            task_description = f"Review the following architecture for data design concerns:\n{description}"
            if data_context:
                task_description += f"\n\nRelevant Data Architecture Knowledge:\n{data_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['data_architecture'],
                expected_output="Data architecture evaluation with identified concerns and recommendations"
            ))
        
        # Cost optimization review task
        if 'cost_optimization' in self.agents:
            cost_context = ""
            if context_manager:
                try:
                    cost_context = context_manager.get_context_for_domain('cost_optimization')
                except Exception as e:
                    print(f"Warning: Could not retrieve cost optimization context: {e}")
            
            task_description = f"Review the following architecture for cost optimization opportunities:\n{description}"
            if cost_context:
                task_description += f"\n\nRelevant Cost Optimization Knowledge:\n{cost_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['cost_optimization'],
                expected_output="Cost analysis with optimization opportunities and savings estimates"
            ))
        
        # Compliance review task
        if 'compliance' in self.agents:
            compliance_context = ""
            if context_manager:
                try:
                    compliance_context = context_manager.get_context_for_domain('compliance')
                except Exception as e:
                    print(f"Warning: Could not retrieve compliance context: {e}")
            
            task_description = f"Review the following architecture for compliance and governance issues:\n{description}"
            if compliance_context:
                task_description += f"\n\nRelevant Compliance Knowledge:\n{compliance_context}"
            
            tasks.append(Task(
                description=task_description,
                agent=self.agents['compliance'],
                expected_output="Compliance evaluation with identified gaps and recommendations"
            ))
        
        return tasks
    
    def build_orchestrator_task(self, review_outputs: str) -> Task:
        """
        Build a task for the orchestrator agent to synthesize review findings
        
        Args:
            review_outputs: Combined outputs from all review agents
            
        Returns:
            Task for orchestrator agent
        """
        orchestrator = self.factory.build_orchestrator()
        
        return Task(
            description=f"Synthesize the following architecture review findings into a final approval decision:\n{review_outputs}",
            agent=orchestrator,
            expected_output="Final approval decision with overall score and rationale"
        )
