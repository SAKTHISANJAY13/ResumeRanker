"""Common scoring and ranking model definitions."""

from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass(frozen=True)
class ComponentScores:
    """Breakdown of individual scoring weights for debugging and explainability."""
    experience_score: float = 0.0
    skills_score: float = 0.0
    jd_alignment_score: float = 0.0
    semantic_alignment_score: float = 0.0
    behavioral_score: float = 0.0
    location_score: float = 0.0
    signals_score: float = 0.0
    anomaly_penalty: float = 0.0

@dataclass
class CandidateScore:
    """Represents a candidate's scored results for Stage-2 output."""
    candidate_id: str
    final_score: float
    component_scores: ComponentScores
    rank: Optional[int] = None
    reasoning: Optional[str] = None
