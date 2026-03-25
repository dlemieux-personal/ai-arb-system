"""
Recommendation Crew Builder Module
Creates and configures the recommendation crew for improvement suggestions.
"""

from crewai import Crew, Agent, Task, Process
from src.agents.definitions.recommendation_agents import (
    build_recommendation_security_agent,
    build_recommendation_scalability_agent,
    build_recommendation_reliability_agent,
    build_recommendation_data_agent,
    build_recommendation_cost_agent,
    build_recommendation_compliance_agent,
)
from src.agents.definitions.recommendation_orchestrator_agent import build_recommendation_orchestrator
from typing import Dict, Any, List, Optional
from pathlib import Path


class RecommendationCrewBuilder:
    """Builder for creating the recommendation crew"""
    
    def __init__(self):
        """Initialize the recommendation crew builder"""
        self.agents = {}
        self.tasks = {}
    
    def build_agents(self) -> Dict[str, Agent]:
        """
        Build all recommendation agents
        
        Returns:
            Dictionary of configured agents
        """
        self.agents = {
            'security': build_recommendation_security_agent(),
            'scalability': build_recommendation_scalability_agent(),
            'reliability': build_recommendation_reliability_agent(),
            'data_architecture': build_recommendation_data_agent(),
            'cost_optimization': build_recommendation_cost_agent(),
            'compliance': build_recommendation_compliance_agent(),
            'orchestrator': build_recommendation_orchestrator(),
        }
        return self.agents
    
    def build_recommendation_crew(self, review_results: str) -> Crew:
        """
        Build the complete recommendation crew with agents and tasks
        
        Args:
            review_results: Combined results from all review agents
            
        Returns:
            Configured Crew instance
        """
        # Ensure agents are built
        if not self.agents:
            self.build_agents()
        
        # Build tasks for each agent based on review results
        tasks = self._create_recommendation_tasks(review_results)
        
        # Create the crew with agents and tasks
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True,
            process=Process.sequential  # Sequential to allow orchestrator to synthesize
        )
        
        return crew
    
    def _create_recommendation_tasks(self, review_results: str) -> List[Task]:
        """
        Create recommendation tasks based on review results
        
        Args:
            review_results: Combined results from all review agents
            
        Returns:
            List of Task instances
        """
        tasks = []
        
        # Security recommendations task
        if 'security' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
security recommendations to address identified vulnerabilities and improve security posture:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Affected components
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Expected impact on security
6. Detailed implementation steps
7. Success criteria for measuring effectiveness
8. Reference to similar patterns or precedents if available
                """,
                agent=self.agents['security'],
                expected_output="Detailed security recommendations with implementation roadmap"
            ))
        
        # Scalability recommendations task
        if 'scalability' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
scalability recommendations to improve system capacity and performance:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Components needing scalability improvements
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Expected performance improvement impact
6. Detailed implementation steps (auto-scaling, load balancing, caching, etc.)
7. Success criteria (throughput, latency targets)
8. Reference to proven scalability patterns
                """,
                agent=self.agents['scalability'],
                expected_output="Detailed scalability recommendations with performance targets"
            ))
        
        # Reliability recommendations task
        if 'reliability' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
reliability recommendations to improve fault tolerance and disaster recovery:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Components requiring reliability improvements
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Expected uptime improvement
6. Detailed implementation steps (redundancy, failover, circuit breakers, etc.)
7. Success criteria (SLA targets, RTO/RPO metrics)
8. Reference to proven reliability patterns
                """,
                agent=self.agents['reliability'],
                expected_output="Detailed reliability recommendations with SLA improvements"
            ))
        
        # Data architecture recommendations task
        if 'data_architecture' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
data architecture recommendations to improve consistency, performance, and data management:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Data components or patterns to improve
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Expected improvements (performance, consistency, scalability)
6. Detailed implementation steps (CQRS, event sourcing, denormalization, etc.)
7. Success criteria (query latency, consistency guarantees)
8. Reference to proven data architecture patterns
                """,
                agent=self.agents['data_architecture'],
                expected_output="Detailed data architecture recommendations with performance metrics"
            ))
        
        # Cost optimization recommendations task
        if 'cost_optimization' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
cost optimization recommendations to reduce cloud spending:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Components or services with optimization opportunities
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Estimated cost savings (monthly/annual)
6. Detailed implementation steps (instance sizing, reserved capacity, spot instances, etc.)
7. Success criteria (cost metrics, ROI timeline)
8. Reference to cloud optimization patterns or best practices
                """,
                agent=self.agents['cost_optimization'],
                expected_output="Detailed cost optimization recommendations with savings projections"
            ))
        
        # Compliance recommendations task
        if 'compliance' in self.agents:
            tasks.append(Task(
                description=f"""
Based on the following architecture review results, generate specific, actionable 
compliance recommendations to achieve regulatory requirements and establish governance controls:

{review_results}

For each recommendation, provide:
1. Clear title and description
2. Regulations and compliance standards addressed
3. Priority (Critical/High/Medium/Low)
4. Implementation effort estimate
5. Expected compliance improvements
6. Detailed implementation steps (controls, audit trails, data governance, etc.)
7. Success criteria (audit readiness, compliance certifications)
8. Reference to compliance frameworks and governance patterns
                """,
                agent=self.agents['compliance'],
                expected_output="Detailed compliance recommendations with governance roadmap"
            ))
        
        # Orchestrator synthesis task (uses all previous recommendations)
        if 'orchestrator' in self.agents:
            tasks.append(Task(
                description=f"""
You are receiving recommendations from specialists across 6 architectural domains. 
Your task is to synthesize these recommendations into a cohesive improvement roadmap.

Original review results:
{review_results}

Your goal is to:

1. SYNTHESIZE: Identify cross-domain dependencies and opportunities where a single 
   improvement addresses multiple domains

2. PRIORITIZE: Create a phased roadmap:
   - Phase 0: Quick wins (low effort, high impact)
   - Phase 1: Foundation (critical items and prerequisites)
   - Phase 2: Enhancement (medium priority items)
   - Phase 3: Long-term (strategic improvements)

3. SEQUENCE: Ensure dependencies are respected and implementation order makes sense

4. QUANTIFY: Estimate total effort, timeline, and ROI

5. EXECUTIVE SUMMARY: Create a 2-3 paragraph executive summary suitable for 
   presenting to leadership, highlighting:
   - The current architectural risks
   - Top 3-5 most impactful improvements
   - Expected business outcomes
   - Implementation timeline and effort

6. ACTION ITEMS: Extract concrete action items with:
   - Clear owner/responsibility
   - Effort estimate
   - Timeline
   - Success criteria
   - Dependencies

Format your response as:
- EXECUTIVE SUMMARY: [2-3 paragraphs]
- QUICK WINS: [List of low-effort, high-impact items]
- PHASE 1 PRIORITIES: [Foundation and critical items]
- PHASE 2 ENHANCEMENTS: [Medium priority improvements]
- PHASE 3 STRATEGIC: [Long-term architectural improvements]
- ACTION ITEMS: [Concrete tasks with owners and timelines]
- TOTAL EFFORT ESTIMATE: [Duration and team size]
                """,
                agent=self.agents['orchestrator'],
                expected_output="Cohesive improvement roadmap with phased execution plan and executive summary"
            ))
        
        return tasks
    
    def extract_orchestrator_summary(self, crew_output: str) -> Dict[str, Any]:
        """
        Extract structured recommendations from crew output
        
        Args:
            crew_output: Raw output from the recommendation crew
            
        Returns:
            Dictionary with structured recommendation data
        """
        # This would parse the crew output and structure it for the PR/SME review
        # For now, return the raw output
        return {
            'raw_output': crew_output,
            'executive_summary': crew_output,
            'recommendations': crew_output,
            'action_items': crew_output,
            'timeline': crew_output,
        }
