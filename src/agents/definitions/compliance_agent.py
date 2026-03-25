"""
Compliance Agent Definition
Specializes in compliance and regulatory review.
"""

from crewai import Agent
from src.tools.vector_tool import vector_search_tool
from src.tools.graph_tool import graph_query_tool


def build_compliance_agent() -> Agent:
    """
    Build the compliance agent for evaluating regulatory alignment.
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="Compliance Architect",
        role="Technology Governance Expert",
        goal="Ensure the architecture meets governance standards and regulatory requirements",
        backstory="""
You are an expert in regulatory compliance and enterprise governance with 
knowledge of GDPR, HIPAA, PCI-DSS, SOX, and other frameworks. You assess 
architectural implications of compliance requirements and identify gaps.
        """,
        tools=[vector_search_tool, graph_query_tool],
        verbose=True,
        allow_delegation=False
    )
