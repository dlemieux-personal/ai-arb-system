"""
Cost Optimization Agent Definition
Specializes in cost optimization review.
"""

from crewai import Agent
from src.tools.vector_tool import vector_search_tool
from src.tools.graph_tool import graph_query_tool


def build_cost_optimization_agent() -> Agent:
    """
    Build the cost optimization agent for evaluating cost efficiency.
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="Cloud Cost Architect",
        role="Cloud Cost Optimization Expert",
        goal="Identify unnecessary cost drivers and recommend cost-efficient alternatives",
        backstory="""
You specialize in cost-efficient cloud architecture with deep knowledge of 
pricing models, reserved instances, spot pricing, and architectural patterns that 
minimize waste. You can quantify cost implications of architectural decisions.
        """,
        tools=[vector_search_tool, graph_query_tool],
        verbose=True,
        allow_delegation=False
    )
