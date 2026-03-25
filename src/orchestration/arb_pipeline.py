"""
ARB Pipeline Module
Main orchestration pipeline for the architecture review process.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from src.orchestration.recommendation_crew_builder import RecommendationCrewBuilder


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
        # Look for executive summary section in the output
        if "EXECUTIVE SUMMARY" in recommendations_output:
            try:
                start = recommendations_output.find("EXECUTIVE SUMMARY")
                end = recommendations_output.find("\n\n", start)
                if end == -1:
                    end = len(recommendations_output)
                return recommendations_output[start:end]
            except Exception:
                return recommendations_output[:500]
        
        # Fallback: return first 500 characters
        return recommendations_output[:500] if recommendations_output else ""
    
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
            # Build and run the review crew
            crew = self.crew_builder.build_review_crew(submission_text)

            # Attempt to execute crew; the real Crew API may differ.
            review_outputs: Dict[str, str] = {}
            if hasattr(crew, 'run'):
                try:
                    review_outputs = crew.run(submission_text)
                except Exception:
                    review_outputs = {}
            # fallback to placeholder outputs if crew invocation failed or is not available
            if not review_outputs:
                # fallback placeholders; use fixed dimension keys to align with scoring
                for dim in ['security', 'scalability', 'reliability',
                            'data_architecture', 'cost_optimization', 'compliance']:
                    score_key = f"{dim.upper()}_SCORE"
                    review_outputs[dim] = f"{score_key}: 0.50"
            context['review_outputs'] = review_outputs
            
            # --- 4. Scoring ----------------------------------------------------------
            # Parse numeric scores from each agent output. For now we assume each
            # output ends with a line like "*_SCORE: X" where X is 0.0-1.0.
            dimension_scores: Dict[str, float] = {}
            for dim, output in review_outputs.items():
                try:
                    # simple parsing logic
                    last_line = output.strip().splitlines()[-1]
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
            
            # --- 5. Approval Decision ------------------------------------------------
            critical_findings = {}  # placeholder for parsing critical issues
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
                recommendations_output = rec_crew.kickoff()
                recommendation_summary = self._extract_executive_summary(recommendations_output)
                
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
