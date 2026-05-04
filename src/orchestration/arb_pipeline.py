"""
ARB Pipeline Module
Main orchestration pipeline for the architecture review process.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from src.orchestration.recommendation_crew_builder import RecommendationCrewBuilder
from src.orchestration.security_orchestrator import create_security_orchestrator
from src.orchestration.scalability_orchestrator import create_scalability_orchestrator
from src.tools.retrieval_context import get_retrieval_context


@dataclass
class PipelineResult:
    """Result of ARB pipeline execution"""
    
    submission_id: str
    status: str  # success, failed
    overall_score: float
    approval_decision: str
    report_path: Optional[Path] = None
    error_message: Optional[str] = None
    recommendations: Optional[str] = None  # Recommendations from recommendation crew
    recommendation_summary: Optional[str] = None  # Executive summary


class ARBPipeline:
    """Main pipeline orchestrating the architecture review"""
    
    def __init__(self, config_path: Path):
        """
        Initialize the ARB pipeline
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        # configuration files for scoring
        self.weights_path = config_path / "scoring_weights.yaml"
        self.thresholds_path = config_path / "scoring_thresholds.yaml"
        self.schema_path = config_path / "schemas" / "architecture_submission_schema.json"
        
        # initialize helper components
        from src.orchestration.crew_builder import CrewBuilder
        from src.scoring.scoring_model import ScoringModel
        from src.scoring.approval_logic import ApprovalEngine
        
        # schema validator (optional)
        self.schema_validator = None
        if self.schema_path.exists():
            try:
                from src.intake.schema_validator import SchemaValidator
                self.schema_validator = SchemaValidator(self.schema_path)
            except ImportError:
                self.schema_validator = None
        
        # the orchestration-level CrewBuilder accepts an optional AgentFactory
        self.crew_builder = CrewBuilder()
        
        # try to load scoring configuration files; fall back to defaults if missing
        try:
            self.scoring_model = ScoringModel(self.weights_path, self.thresholds_path)
            thresholds = self.scoring_model.thresholds
        except FileNotFoundError:
            # create a minimal scoring model with equal weights and default thresholds
            self.scoring_model = ScoringModel.__new__(ScoringModel)
            # six dimensions by default
            default_dims = ['security', 'scalability', 'reliability',
                            'data_architecture', 'cost_optimization', 'compliance']
            self.scoring_model.weights = {dim: 1 / len(default_dims) for dim in default_dims}
            self.scoring_model.thresholds = {
                'thresholds': {
                    'overall_score': {
                        'approved': {'minimum': 0.80},
                        'conditional_approval': {'minimum': 0.65}
                    }
                }
            }
            thresholds = self.scoring_model.thresholds
        
        self.approval_engine = ApprovalEngine(thresholds)
    
    def _extract_executive_summary(self, recommendations_output: str) -> str:
        """
        Extract executive summary from recommendation crew output
        
        Args:
            recommendations_output: Raw output from recommendation crew
            
        Returns:
            Executive summary string
        """
        # Convert to string if needed (CrewOutput object)
        output_str = str(recommendations_output) if recommendations_output else ""
        
        # Look for executive summary section in the output
        if "EXECUTIVE SUMMARY" in output_str:
            try:
                start = output_str.find("EXECUTIVE SUMMARY")
                end = output_str.find("\n\n", start)
                if end == -1:
                    end = len(output_str)
                return output_str[start:end]
            except Exception:
                return output_str[:500]
        
        # Fallback: return first 500 characters
        return output_str[:500] if output_str else ""
    
    def process_submission(self, submission_path: Path) -> PipelineResult:
        """
        Process a submission through the entire review pipeline
        
        Args:
            submission_path: Path to submission file
            
        Returns:
            PipelineResult object
        """
        submission_id = submission_path.stem
        try:
            # --- 1. Submission Intake ------------------------------------------------
            with open(submission_path, 'r', encoding='utf-8') as f:
                submission_text = f.read()
            context: Dict[str, Any] = {'submission_id': submission_id,
                                       'submission_text': submission_text}
            
            # --- 2. Schema Validation ------------------------------------------------
            if self.schema_validator:
                # attempt to parse submission as JSON
                try:
                    import json
                    submission_dict = json.loads(submission_text)
                except Exception:
                    submission_dict = None
                if submission_dict is not None:
                    valid, errors = self.schema_validator.validate(submission_dict)
                    context['schema_valid'] = valid
                    context['schema_errors'] = errors
                else:
                    context['schema_valid'] = False
                    context['schema_errors'] = [
                        "Submission text is not valid JSON for schema validation"
                    ]
                # halt pipeline immediately if schema invalid
                if not context['schema_valid']:
                    return PipelineResult(
                        submission_id=submission_id,
                        status='failed',
                        overall_score=0.0,
                        approval_decision='schema_validation_failed',
                        error_message='; '.join(context.get('schema_errors', []))
                    )
            else:
                # no schema available, skip validation
                context['schema_valid'] = True
            
            # --- 3. Agent Review -----------------------------------------------------
            # Build and run the review crew using structured orchestration
            review_outputs: Dict[str, Any] = {}
            
            # Run security agent using orchestrator for structured output
            try:
                security_orchestrator = create_security_orchestrator()
                retrieval_context = None
                try:
                    ctx_manager = get_retrieval_context(submission_text)
                    retrieval_context = ctx_manager.get_context_for_domain('security')
                except Exception:
                    # Retrieval context is optional
                    retrieval_context = None
                
                security_output = security_orchestrator.run_crew(
                    architecture_description=submission_text,
                    submission_id=submission_id,
                    retrieval_context=retrieval_context
                )
                review_outputs['security'] = security_output
                context['security_task_output'] = security_output
            except Exception as e:
                print(f"Warning: Security orchestration failed: {e}")
                # Create default security output
                from src.schemas.agent_outputs import SecurityAgentOutput
                from src.orchestration.task_specs import SecurityTaskOutput
                review_outputs['security'] = SecurityTaskOutput(
                    agent_output=SecurityAgentOutput(
                        findings=[],
                        recommendations=[],
                        security_score=0.50,
                        confidence=0.0,
                        summary="Security review failed"
                    ),
                    raw_output="",
                    parsing_successful=False,
                    parsing_error=str(e)
                )
            
            # Run other agents via crew for now (to be updated in subsequent PRs)
            crew = self.crew_builder.build_review_crew(submission_text)
            
            # Attempt to execute crew; the real Crew API may differ.
            crew_result: Any = None
            if hasattr(crew, 'kickoff'):
                try:
                    crew_result = crew.kickoff()
                except Exception as e:
                    print(f"Warning: Crew execution failed: {e}")
                    crew_result = None
            
            # Convert crew result to string for processing
            crew_output_str = str(crew_result) if crew_result else ""
            
            # Add crew outputs for non-security agents
            # For now, we use fallback placeholders since crew doesn't return structured dict
            for dim in ['scalability', 'reliability', 'data_architecture', 'cost_optimization', 'compliance']:
                # fallback placeholder
                score_key = f"{dim.upper()}_SCORE"
                review_outputs[dim] = f"{score_key}: 0.50"
            
            context['review_outputs'] = review_outputs
            
            # --- 4. Scoring ----------------------------------------------------------
            # Parse scores from agent outputs
            # Security agent provides structured output via orchestrator
            # Other agents provide string outputs via crew (for now)
            dimension_scores: Dict[str, float] = {}
            critical_findings: Dict[str, List[str]] = {}
            
            for dim, output in review_outputs.items():
                if dim == 'security':
                    # Handle structured SecurityTaskOutput from orchestrator
                    try:
                        from src.orchestration.task_specs import SecurityTaskOutput
                        if isinstance(output, SecurityTaskOutput):
                            security_orchestrator = create_security_orchestrator()
                            dim_score = security_orchestrator.extract_dimension_score(output)
                            dimension_scores[dim] = dim_score.score
                            critical_findings[dim] = dim_score.critical_issues
                        else:
                            dimension_scores[dim] = 0.50
                    except Exception:
                        dimension_scores[dim] = 0.50
                else:
                    # Handle string outputs from crew
                    try:
                        # simple parsing logic for crew outputs
                        output_str = str(output) if output else ""
                        last_line = output_str.strip().splitlines()[-1] if output_str else ""
                        if ':' in last_line:
                            _, val = last_line.split(':', 1)
                            dimension_scores[dim] = float(val.strip())
                        else:
                            dimension_scores[dim] = 0.0
                    except Exception:
                        dimension_scores[dim] = 0.0
            
            overall = self.scoring_model.calculate_overall_score(dimension_scores)
            recommendation = self.scoring_model.determine_recommendation(overall)
            context['dimension_scores'] = dimension_scores
            context['overall_score'] = overall
            context['recommendation'] = recommendation
            context['critical_findings'] = critical_findings
            approval = self.approval_engine.make_decision(
                overall_score=overall,
                dimension_scores=dimension_scores,
                critical_findings=critical_findings
            )
            context['approval'] = approval
            
            # --- 6. Recommendation Generation & Report ------------------------------
            # Use recommendation crew to generate improvement suggestions
            recommendations_output = None
            recommendation_summary = None
            
            try:
                recommendation_builder = RecommendationCrewBuilder()
                recommendation_builder.build_agents()
                
                # Prepare review results for recommendation crew
                review_summary = "ARCHITECTURE REVIEW FINDINGS:\n"
                for dim, output in review_outputs.items():
                    score = dimension_scores.get(dim, 0.0)
                    review_summary += f"\n{dim.upper()} (Score: {score:.2f}):\n{output[:500]}\n"
                
                # Build and execute recommendation crew
                rec_crew = recommendation_builder.build_recommendation_crew(review_summary)
                crew_output = rec_crew.kickoff()
                recommendations_output = str(crew_output) if crew_output else None
                recommendation_summary = self._extract_executive_summary(recommendations_output) if recommendations_output else None
                
                context['recommendations'] = recommendations_output
                context['recommendation_summary'] = recommendation_summary
            except Exception as e:
                # If recommendation generation fails, continue with review results only
                print(f"Warning: Recommendation generation failed: {e}")
                recommendations_output = None
                recommendation_summary = None
            
            report_path = None
            
            # --- 7. Archival ---------------------------------------------------------
            # Archive submission and results (not implemented)

            return PipelineResult(
                submission_id=submission_id,
                status='success',
                overall_score=overall,
                approval_decision=approval.status,
                report_path=report_path,
                recommendations=recommendations_output,
                recommendation_summary=recommendation_summary
            )

        except Exception as e:
            return PipelineResult(
                submission_id=submission_id,
                status='failed',
                overall_score=0.0,
                approval_decision='error',
                error_message=str(e)
            )
