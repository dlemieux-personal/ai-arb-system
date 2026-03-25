"""
Data Architecture Agent Definition
Specializes in data architecture review.
"""

from crewai import Agent
from src.tools.vector_tool import vector_search_tool
from src.tools.graph_tool import graph_query_tool


def build_data_architecture_agent() -> Agent:
    """
    Build the data architecture agent for evaluating data strategies.
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="Data Architect",
        role="Enterprise Data Architect",
        goal="Evaluate the architecture's data strategy, consistency models, and storage solutions",
        backstory="""
You are an expert in data modeling, streaming systems, data lakes, and analytics 
pipelines. You understand CAP theorem trade-offs, consistency models, and can 
evaluate both SQL and NoSQL database choices within context.
        """,
        tools=[vector_search_tool, graph_query_tool],
        verbose=True,
        allow_delegation=False
    )
