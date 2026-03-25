"""
Test Agent Reviews Module
Tests for agent review functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.agents.definitions.security_agent import build_security_agent
from src.agents.definitions.scalability_agent import build_scalability_agent


class TestSecurityAgent:
    """Tests for security review agent"""
    
    @pytest.fixture
    def security_agent(self):
        """Fixture for initializing security agent"""
        return build_security_agent()
    
    def test_agent_initialization(self, security_agent):
        """Test agent is properly initialized"""
        assert security_agent.role == "Senior Cloud Security Architect"
        assert security_agent.goal is not None
        assert "security" in security_agent.goal.lower()
    
    def test_agent_has_tools(self, security_agent):
        """Test agent has required tools configured"""
        assert len(security_agent.tools) >= 2


class TestScalabilityAgent:
    """Tests for scalability review agent"""
    
    @pytest.fixture
    def scalability_agent(self):
        """Fixture for initializing scalability agent"""
        return build_scalability_agent()
    
    def test_agent_initialization(self, scalability_agent):
        """Test agent is properly initialized"""
        assert scalability_agent.role == "Distributed Systems Architect"
        assert scalability_agent.goal is not None
        assert "scale" in scalability_agent.goal.lower()
