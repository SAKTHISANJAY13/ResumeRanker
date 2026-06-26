"""Weighted scoring module for Stage-2 reranking."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from src.utils.logger import Logger
from src.common.score import CandidateScore, ComponentScores
from stage2.feature_engineering.experience import ExperienceFeatureResult
from stage2.feature_engineering.skills import SkillsFeatureResult
from stage2.feature_engineering.jd_alignment import JdAlignmentFeatureResult
from stage2.feature_engineering.behavioral import BehavioralFeatureResult
from stage2.feature_engineering.location import LocationFeatureResult
from stage2.feature_engineering.anomaly import AnomalyFeatureResult

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.weights import (
        STAGE2_GLOBAL_WEIGHTS,
        EXPERIENCE_SUB_WEIGHTS,
        SKILLS_SUB_WEIGHTS,
        ALIGNMENT_SUB_WEIGHTS
    )
except ImportError:
    # Production-grade fallback weights for the final scoring ensemble
    STAGE2_GLOBAL_WEIGHTS = {
        "experience": 0.25,
        "skills": 0.25,
        "alignment": 0.15,
        "semantic": 0.15,
        "behavior": 0.10,
        "location": 0.10,
        "penalty_multiplier": 0.05  # Multiplied by anomaly penalty score
    }
    
    EXPERIENCE_SUB_WEIGHTS = {
        "tenure_suitability": 0.40,
        "ai_exp": 0.20,
        "prod_ml_exp": 0.15,
        "ret_exp": 0.10,
        "rank_exp": 0.10,
        "rec_exp": 0.05
    }
    
    SKILLS_SUB_WEIGHTS = {
        "required_coverage": 0.50,
        "preferred_coverage": 0.30,
        "bonus_match": 0.20,
        "penalty_deduction": 0.15
    }
    
    ALIGNMENT_SUB_WEIGHTS = {
        "retrieval_fit": 0.15,
        "ranking_fit": 0.15,
        "vector_database_fit": 0.15,
        "evaluation_fit": 0.10,
        "python_fit": 0.10,
        "startup_fit": 0.15,
        "product_engineering_fit": 0.10,
        "shipping_mindset_fit": 0.10
    }

# Experience scaling constraints
OPTIMAL_EXP_MIN = 4.0
OPTIMAL_EXP_MAX = 10.0
MID_LOW_EXP_MIN = 2.0
HIGH_EXP_MAX = 15.0

# Max scale bounds
ALIGNMENT_MAX_BOUND = 25.0
MAX_BONUS_SKILLS = 3.0

class WeightedScorer:
    """Combines candidate feature results into a standardized, component-backed final score."""

    def __init__(self) -> None:
        self.global_weights = STAGE2_GLOBAL_WEIGHTS
        self.exp_weights = EXPERIENCE_SUB_WEIGHTS
        self.skills_weights = SKILLS_SUB_WEIGHTS
        self.align_weights = ALIGNMENT_SUB_WEIGHTS

    def _score_experience(self, exp: ExperienceFeatureResult) -> float:
        """Scores experience dimension (combines target tenure fit and domain matches)."""
        # 1. Target tenure suitability (JD optimal bounds: 4-10 years)
        tenure = exp.total_experience
        if OPTIMAL_EXP_MIN <= tenure <= OPTIMAL_EXP_MAX:
            tenure_fit = 1.0
        elif MID_LOW_EXP_MIN <= tenure < OPTIMAL_EXP_MIN:
            tenure_fit = 0.5
        elif OPTIMAL_EXP_MAX < tenure <= HIGH_EXP_MAX:
            tenure_fit = 0.4
        else:
            tenure_fit = 0.0

        # 2. Domain specialized expertise years
        ai_score = min(exp.ai_experience / 5.0, 1.0)
        prod_ml_score = min(exp.production_ml_experience / 3.0, 1.0)
        ret_score = min(exp.retrieval_experience / 3.0, 1.0)
        rank_score = min(exp.ranking_experience / 3.0, 1.0)
        rec_score = min(exp.recommendation_experience / 3.0, 1.0)

        # 3. Combine sub-components
        exp_score = (
            tenure_fit * self.exp_weights.get("tenure_suitability", 0.0) +
            ai_score * self.exp_weights.get("ai_exp", 0.0) +
            prod_ml_score * self.exp_weights.get("prod_ml_exp", 0.0) +
            ret_score * self.exp_weights.get("ret_exp", 0.0) +
            rank_score * self.exp_weights.get("rank_exp", 0.0) +
            rec_score * self.exp_weights.get("rec_exp", 0.0)
        )
        return float(exp_score)

    def _score_skills(self, skills: SkillsFeatureResult) -> float:
        """Scores skills coverage and matching density."""
        bonus_score = min(skills.bonus_matched_count / MAX_BONUS_SKILLS, 1.0)
        
        skills_score = (
            skills.required_coverage_ratio * self.skills_weights.get("required_coverage", 0.0) +
            skills.preferred_coverage_ratio * self.skills_weights.get("preferred_coverage", 0.0) +
            bonus_score * self.skills_weights.get("bonus_match", 0.0) -
            (skills.penalty_matched_count * self.skills_weights.get("penalty_deduction", 0.0))
        )
        return float(max(0.0, min(skills_score, 1.0)))

    def _score_alignment(self, align: JdAlignmentFeatureResult) -> float:
        """Scores candidate's overall JD alignment fit across all semantic axes."""
        raw_score = (
            align.retrieval_fit * self.align_weights.get("retrieval_fit", 0.0) +
            align.ranking_fit * self.align_weights.get("ranking_fit", 0.0) +
            align.vector_database_fit * self.align_weights.get("vector_database_fit", 0.0) +
            align.evaluation_fit * self.align_weights.get("evaluation_fit", 0.0) +
            align.python_fit * self.align_weights.get("python_fit", 0.0) +
            align.startup_fit * self.align_weights.get("startup_fit", 0.0) +
            align.product_engineering_fit * self.align_weights.get("product_engineering_fit", 0.0) +
            align.shipping_mindset_fit * self.align_weights.get("shipping_mindset_fit", 0.0)
        )
        # Normalize alignment score relative to maximum expected bounds
        return float(max(0.0, min(raw_score / ALIGNMENT_MAX_BOUND, 1.0)))

    def compute_candidate_score(
        self,
        candidate_id: str,
        exp: ExperienceFeatureResult,
        skills: SkillsFeatureResult,
        align: JdAlignmentFeatureResult,
        behavior: BehavioralFeatureResult,
        location: LocationFeatureResult,
        anomaly: AnomalyFeatureResult,
        semantic_score: float = 0.0
    ) -> CandidateScore:
        """Orchestrates compilation of sub-scores and aggregates them into the final candidate rating."""
        Logger.info(f"Computing weighted score for candidate {candidate_id}")

        # Compute individual dimension scores (all normalized between 0.0 and 1.0)
        s_exp = self._score_experience(exp)
        s_skills = self._score_skills(skills)
        s_align = self._score_alignment(align)
        s_semantic = semantic_score
        s_behavior = behavior.overall_behavioral_score
        s_location = location.overall_location_score
        
        # Anomaly penalties are represented as a raw positive number indicating risk degree
        s_anomaly_penalty = anomaly.penalty_score

        # Weighted combination of positive parameters
        positive_score = (
            s_exp * self.global_weights.get("experience", 0.0) +
            s_skills * self.global_weights.get("skills", 0.0) +
            s_align * self.global_weights.get("alignment", 0.0) +
            s_semantic * self.global_weights.get("semantic", 0.0) +
            s_behavior * self.global_weights.get("behavior", 0.0) +
            s_location * self.global_weights.get("location", 0.0)
        )

        # Apply negative penalty multiplier (using a multiplicative decay as recommended)
        # A penalty_multiplier of 0.05 means a penalty of 10.0 reduces score by 50%.
        penalty_decay = min(1.0, s_anomaly_penalty * self.global_weights.get("penalty_multiplier", 0.0))
        final_score = float(max(0.0, positive_score * (1.0 - penalty_decay)))

        # Build component scores breakdown (critical for explainability/reasoning)
        component_breakdown = ComponentScores(
            experience_score=s_exp,
            skills_score=s_skills,
            jd_alignment_score=s_align,
            semantic_alignment_score=s_semantic,
            behavioral_score=s_behavior,
            location_score=s_location,
            anomaly_penalty=s_anomaly_penalty
        )

        return CandidateScore(
            candidate_id=candidate_id,
            final_score=final_score,
            component_scores=component_breakdown
        )
