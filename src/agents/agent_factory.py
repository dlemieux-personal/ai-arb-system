"""
Agent Factory Module
Creates and configures agent instances using builder functions.
"""

from crewai import Agent
from src.agents.definitions.orchestrator_agent import build_orchestrator_agent
from src.agents.definitions.security_agent import build_security_agent
from src.agents.definitions.scalability_agent import build_scalability_agent
from src.agents.definitions.reliability_agent import build_reliability_agent
from src.agents.definitions.data_architecture_agent import build_data_architecture_agent
from src.agents.definitions.cost_optimization_agent import build_cost_optimization_agent
from src.agents.definitions.compliance_agent import build_compliance_agent
from typing import Dict, Any, Optional
from pathlib import Path
import yaml


class AgentFactory:
    """Factory for creating agent instances using builder functions"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the agent factory
        
        Args:
            config_path: Optional path to agent configuration file (for future use)
        """
        self.config_path = config_path
        self.config = self._load_config() if config_path else {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        if not self.config_path:
            return {}
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def build_orchestrator(self) -> Agent:
        """
        Build the orchestrator agent
        
        Returns:
            Configured Orchestrator Agent instance
        """
        return build_orchestrator_agent()
    
    def create_all_review_agents(self) -> Dict[str, Agent]:
        """
        Create all review agents using their builder functions
        
        Returns:
            Dictionary mapping agent names to agent instances
        """
        agents = {
            'security': build_security_agent(),
            'scalability': build_scalability_agent(),
            'reliability': build_reliability_agent(),
            'data_architecture': build_data_architecture_agent(),
            'cost_optimization': build_cost_optimization_agent(),
            'compliance': build_compliance_agent(),
        }
        
        return agents
