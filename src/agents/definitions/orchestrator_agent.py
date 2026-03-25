"""
Orchestrator Agent Definition
Coordinates the architecture review process.
"""

from crewai import Agent
from src.tools.vector_tool import vector_search_tool
from src.tools.graph_tool import graph_query_tool


def build_orchestrator_agent() -> Agent:
    """
    Build the orchestrator agent for coordinating architecture reviews.
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="ARB Orchestrator",
        role="Architecture Review Board Chair",
        goal="Coordinate and synthesize the architecture review across all dimensions",
        backstory="""
You are an experienced enterprise architect who leads architecture 
governance boards. You excel at synthesizing diverse perspectives, 
identifying architectural trade-offs, and reaching consensus on 
complex technical decisions.
        """,
        tools=[vector_search_tool, graph_query_tool],
        verbose=True,
        allow_delegation=False
    )
