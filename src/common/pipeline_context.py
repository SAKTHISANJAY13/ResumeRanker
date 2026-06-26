"""Common pipeline execution context definition."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class JobDescriptionParsed:
    """Structured representation of the parsed target Job Description."""
    title: str = ""
    min_years_experience: float = 0.0
    max_years_experience: float = 0.0
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    target_locations: List[str] = field(default_factory=list)
    preferred_work_modes: List[str] = field(default_factory=list)

@dataclass
class PipelineExecutionStats:
    """Statistics collected during the Stage-2 reranking run."""
    total_candidates_loaded: int = 0
    total_features_extracted: int = 0
    total_candidates_scored: int = 0
    failed_extractions: int = 0
    elapsed_time_seconds: float = 0.0
    peak_memory_mb: float = 0.0

@dataclass
class PipelineContext:
    """Shared context storing configuration, parsed JD, and runtime metrics."""
    job_description: JobDescriptionParsed = field(default_factory=JobDescriptionParsed)
    stats: PipelineExecutionStats = field(default_factory=PipelineExecutionStats)
    meta_info: Dict[str, Any] = field(default_factory=dict)
    
    # Calibration helper properties
    global_min_score: float = float('inf')
    global_max_score: float = float('-inf')
    
    # Logs/Errors collected during pipeline execution
    execution_warnings: List[str] = field(default_factory=list)
