"""Job Description alignment feature engineering module for Stage-2 reranking."""

import re
from dataclasses import dataclass
from typing import List, Dict, Set, Any, Optional
from src.utils.logger import Logger
from stage2.feature_engineering.base import BaseFeatureExtractor
from stage2.feature_engineering.utils import extract_career_history

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.keywords import (
        RETRIEVAL_CONCEPT_WORDS,
        RANKING_CONCEPT_WORDS,
        VECTOR_DB_CONCEPT_WORDS,
        EVALUATION_CONCEPT_WORDS,
        PYTHON_CONCEPT_WORDS,
        STARTUP_CONCEPT_WORDS,
        PRODUCT_ENG_CONCEPT_WORDS,
        SHIPPING_CONCEPT_WORDS
    )
except ImportError:
    # Production-grade fallback constants representing key JD pillars
    RETRIEVAL_CONCEPT_WORDS = [
        "retrieval", "search", "indexing", "inverted index", "bm25", "tf-idf", 
        "dense passage retrieval", "dpr", "neural search", "semantic search", 
        "information retrieval", "hybrid search", "lexical search", "solr", "opensearch", "elasticsearch"
    ]
    RANKING_CONCEPT_WORDS = [
        "ranking", "reranking", "cross-encoder", "learning to rank", "ltr", 
        "pairwise ranking", "listwise ranking", "gbdt", "xgboost", "lightgbm", 
        "rrf", "reciprocal rank fusion", "score fusion", "colbert"
    ]
    VECTOR_DB_CONCEPT_WORDS = [
        "vector database", "vector search", "embeddings", "milvus", "pinecone", 
        "qdrant", "weaviate", "faiss", "chroma", "pgvector", "ann", 
        "approximate nearest neighbor", "hnsw", "vector index"
    ]
    EVALUATION_CONCEPT_WORDS = [
        "evaluation", "offline evaluation", "online evaluation", "ab testing", 
        "a/b testing", "metrics", "ndcg", "mrr", "map", "precision@k", 
        "recall@k", "click-through rate", "ctr", "user engagement", "relevance assessment"
    ]
    PYTHON_CONCEPT_WORDS = [
        "python", "pytorch", "tensorflow", "pandas", "numpy", "fastapi", 
        "flask", "django", "scipy", "pythonic"
    ]
    STARTUP_CONCEPT_WORDS = [
        "startup", "early-stage", "founder", "founding", "seed stage", 
        "fast-paced", "scale-up", "hyper-growth", "equity", "bootstrapped"
    ]
    PRODUCT_ENG_CONCEPT_WORDS = [
        "product engineering", "product development", "user-facing", "client-facing", 
        "saas", "b2b", "b2c", "product scaling", "user growth", "business logic",
        "api development", "backend integration"
    ]
    SHIPPING_CONCEPT_WORDS = [
        "shipped", "deployed", "launched", "delivered", "iteration", "end-to-end", 
        "production", "release", "production-ready", "ci/cd", "continuous integration",
        "ci cd", "production deployment"
    ]

# Scoring Weights
TITLE_WEIGHT = 3.0
SKILL_WEIGHT = 2.0
SUMMARY_WEIGHT = 1.5
DESCRIPTION_WEIGHT = 1.0
STARTUP_SIZE_BONUS = 2.0

# Fallback duration in months if missing (equal to 6 months)
DEFAULT_JOB_DURATION_MONTHS = 6.0

@dataclass(frozen=True)
class JdAlignmentFeatureResult:
    """Advanced semantic fit features computed against JD concepts."""
    retrieval_fit: float
    ranking_fit: float
    vector_database_fit: float
    evaluation_fit: float
    python_fit: float
    startup_fit: float
    product_engineering_fit: float
    shipping_mindset_fit: float


class JdAlignmentFeatureExtractor(BaseFeatureExtractor):
    """Extracts alignment metrics using term matches weighted by career duration."""

    def __init__(self) -> None:
        # Precompile regex matches for optimal performance
        self.retrieval_regex = self._compile_regex(RETRIEVAL_CONCEPT_WORDS)
        self.ranking_regex = self._compile_regex(RANKING_CONCEPT_WORDS)
        self.vector_db_regex = self._compile_regex(VECTOR_DB_CONCEPT_WORDS)
        self.evaluation_regex = self._compile_regex(EVALUATION_CONCEPT_WORDS)
        self.python_regex = self._compile_regex(PYTHON_CONCEPT_WORDS)
        self.startup_regex = self._compile_regex(STARTUP_CONCEPT_WORDS)
        self.product_eng_regex = self._compile_regex(PRODUCT_ENG_CONCEPT_WORDS)
        self.shipping_regex = self._compile_regex(SHIPPING_CONCEPT_WORDS)

    def _compile_regex(self, keywords: List[str]) -> re.Pattern:
        """Compiles case-insensitive word-boundary regex for a keyword list."""
        sorted_kws = sorted(keywords, key=len, reverse=True)
        pattern_str = r"\b(" + "|".join(re.escape(kw.lower()) for kw in sorted_kws) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)

    def _compute_fit(
        self, 
        candidate: Dict[str, Any], 
        regex: re.Pattern, 
        check_startup_size: bool = False
    ) -> float:
        """Accumulates fit score based on presence of terms weighted by job duration."""
        score = 0.0

        # 1. Headline & Summary matching
        profile = candidate.get("profile") or {}
        headline = str(profile.get("headline") or "")
        summary = str(profile.get("summary") or "")
        if regex.search(headline) or regex.search(summary):
            score += SUMMARY_WEIGHT

        # 2. Skills list matching
        skills = candidate.get("skills") or []
        for skill in skills:
            skill_name = ""
            if isinstance(skill, str):
                skill_name = skill
            elif isinstance(skill, dict):
                skill_name = skill.get("name") or skill.get("title") or ""
            
            if skill_name and regex.search(skill_name):
                score += SKILL_WEIGHT

        # 3. Career history matching (weighted by duration in years)
        experiences = extract_career_history(candidate)

        if experiences:
            for exp in experiences:
                if not isinstance(exp, dict):
                    continue

                title = str(exp.get("title") or "")
                description = str(exp.get("description") or "")
                company_size = str(exp.get("company_size") or "")

                # Calculate duration in years
                duration_months = exp.get("duration_months")
                if duration_months is None:
                    duration_months = DEFAULT_JOB_DURATION_MONTHS
                try:
                    duration_years = float(duration_months) / 12.0
                except (ValueError, TypeError):
                    duration_years = DEFAULT_JOB_DURATION_MONTHS / 12.0

                # Check title match (highest career weight)
                if regex.search(title):
                    score += TITLE_WEIGHT * (1.0 + duration_years)

                # Check description match
                if regex.search(description):
                    score += DESCRIPTION_WEIGHT * (1.0 + duration_years)

                # Startup-specific company size bonus
                if check_startup_size and company_size in ("1-10", "11-50", "51-200"):
                    score += STARTUP_SIZE_BONUS * duration_years

        # Return raw accumulated fit score
        return float(score)

    def extract_features(self, candidate: Dict[str, Any]) -> JdAlignmentFeatureResult:
        """Extracts all JD alignment features for a candidate."""
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Extracting JD alignment features for candidate {candidate_id}")

        return JdAlignmentFeatureResult(
            retrieval_fit=self._compute_fit(candidate, self.retrieval_regex),
            ranking_fit=self._compute_fit(candidate, self.ranking_regex),
            vector_database_fit=self._compute_fit(candidate, self.vector_db_regex),
            evaluation_fit=self._compute_fit(candidate, self.evaluation_regex),
            python_fit=self._compute_fit(candidate, self.python_regex),
            startup_fit=self._compute_fit(candidate, self.startup_regex, check_startup_size=True),
            product_engineering_fit=self._compute_fit(candidate, self.product_eng_regex),
            shipping_mindset_fit=self._compute_fit(candidate, self.shipping_regex)
        )
