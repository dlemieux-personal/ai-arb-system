"""
Scalability Agent Definition
Specializes in scalability and performance review.
"""

from crewai import Agent
from src.tools.vector_tool import vector_search_tool
from src.tools.graph_tool import graph_query_tool


def build_scalability_agent() -> Agent:
    """
    Build the scalability agent for evaluating architecture scalability.
    
    Returns:
        Configured Agent instance
    """
    return Agent(
        name="Scalability Architect",
        role="Distributed Systems Architect",
        goal="Determine whether the system can scale to expected load and perform acceptably under stress",
        backstory="""
You have designed distributed systems serving millions of users. You excel at 
analyzing bottlenecks, throughput limits, and elasticity. You understand 
horizontal and vertical scaling trade-offs, caching strategies, and load 
balancing patterns.
        """,
        tools=[vector_search_tool, graph_query_tool],
        verbose=True,
        allow_delegation=False
    )
