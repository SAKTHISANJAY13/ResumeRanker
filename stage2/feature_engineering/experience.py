\"\"\"Advanced experience feature engineering module for Stage-2 reranking.\"\"\"

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Any, Tuple, Optional
from src.utils.logger import Logger

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.keywords import (
        AI_KEYWORDS,
        PRODUCT_COMPANIES,
        PRODUCTION_ML_KEYWORDS,
        RETRIEVAL_KEYWORDS,
        RANKING_KEYWORDS,
        RECOMMENDATION_KEYWORDS
    )
except ImportError:
    # Production-grade fallback constants if configs are not yet created
    AI_KEYWORDS = [
        "ai", "artificial intelligence", "machine learning", "ml", "deep learning", 
        "nlp", "llm", "neural network", "computer vision", "transformers", "pytorch", 
        "tensorflow", "keras", "scikit-learn"
    ]
    PRODUCT_COMPANIES = [
        "google", "meta", "facebook", "apple", "amazon", "netflix", "microsoft", 
        "linkedin", "uber", "lyft", "stripe", "airbnb", "twitter", "salesforce", 
        "adobe", "atlassian", "spotify", "zoom", "nvidia", "openai", "anthropic"
    ]
    PRODUCTION_ML_KEYWORDS = [
        "production", "deploy", "scale", "kubernetes", "k8s", "docker", "onnx", 
        "tensorrt", "triton", "mlops", "ci/cd", "monitoring", "latency", 
        "throughput", "optimization", "inference pipeline"
    ]
    RETRIEVAL_KEYWORDS = [
        "retrieval", "search", "elasticsearch", "opensearch", "faiss", "milvus", 
        "pinecone", "qdrant", "weaviate", "hybrid retrieval", "dense retrieval", 
        "sparse retrieval", "vector database", "information retrieval"
    ]
    RANKING_KEYWORDS = [
        "ranking", "reranking", "learning to rank", "ltr", "ndcg", "mrr", "map", 
        "pairwise", "listwise", "ranker", "scoring pipeline"
    ]
    RECOMMENDATION_KEYWORDS = [
        "recommendation", "recommender", "collaborative filtering", "matrix factorization", 
        "two-tower", "personalization", "candidate generation"
    ]

# Days in a standard year for conversion
DAYS_PER_YEAR = 365.25

@dataclass(frozen=True)
class ExperienceFeatureResult:
    \"\"\"Advanced experience metrics computed for a candidate profile.\"\"\"
    total_experience: float
    ai_experience: float
    product_company_experience: float
    production_ml_experience: float
    retrieval_experience: float
    ranking_experience: float
    recommendation_experience: float


class ExperienceFeatureExtractor:
    \"\"\"Extracts advanced experience features using date-interval merging to avoid overlap.\"\"\"

    def __init__(self) -> None:
        # Precompile regex matches for optimal performance
        self.ai_regex = self._compile_regex(AI_KEYWORDS)
        self.production_ml_regex = self._compile_regex(PRODUCTION_ML_KEYWORDS)
        self.retrieval_regex = self._compile_regex(RETRIEVAL_KEYWORDS)
        self.ranking_regex = self._compile_regex(RANKING_KEYWORDS)
        self.recommendation_regex = self._compile_regex(RECOMMENDATION_KEYWORDS)
        self.product_companies = [pc.lower() for pc in PRODUCT_COMPANIES]

    def _compile_regex(self, keywords: List[str]) -> re.Pattern:
        \"\"\"Compiles case-insensitive word-boundary regex for a keyword list.\"\"\"
        sorted_kws = sorted(keywords, key=len, reverse=True)
        pattern_str = r"\b(" + "|".join(re.escape(kw.lower()) for kw in sorted_kws) + r")\b"
        return re.compile(pattern_str, re.IGNORECASE)

    def _parse_date(self, date_str: Any) -> Optional[date]:
        \"\"\"Parses candidate career date strings into datetime.date objects.\"\"\"
        if not date_str:
            return None
        if isinstance(date_str, date):
            return date_str
        if isinstance(date_str, datetime):
            return date_str.date()

        clean_str = str(date_str).strip().lower()
        if clean_str in ("present", "current", "now", "ongoing", "active"):
            return date.today()

        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y/%m/%d", "%Y/%m", "%Y"):
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue

        # Extract 4-digit year as fallback
        match = re.search(r"\b(19|20)\d{2}\b", clean_str)
        if match:
            return date(year=int(match.group(0)), month=1, day=1)

        return None

    def _merge_intervals(self, intervals: List[Tuple[date, date]]) -> float:
        \"\"\"Merges overlapping and adjacent date intervals to calculate unique years.\"\"\"
        if not intervals:
            return 0.0

        sorted_intervals = sorted(intervals, key=lambda x: x[0])
        merged: List[Tuple[date, date]] = []

        for start, end in sorted_intervals:
            if not merged:
                merged.append((start, end))
            else:
                last_start, last_end = merged[-1]
                if start <= last_end:
                    merged[-1] = (last_start, max(last_end, end))
                else:
                    merged.append((start, end))

        total_days = sum((end - start).days for start, end in merged)
        return max(0.0, total_days / DAYS_PER_YEAR)

    def extract_features(self, candidate: Dict[str, Any]) -> ExperienceFeatureResult:
        \"\"\"Extracts advanced experience features for a single candidate profile.\"\"\"
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Extracting experience features for candidate {candidate_id}")

        # Check for direct years of experience as fallback total
        direct_total_years = 0.0
        for key in ("years_of_experience", "total_experience_years"):
            val = candidate.get(key)
            if val is not None:
                try:
                    direct_total_years = float(val)
                    break
                except (ValueError, TypeError):
                    pass

        # Try to locate the career history
        experiences = None
        for key in ("career_history", "experience", "experiences", "work_history"):
            val = candidate.get(key)
            if isinstance(val, list):
                experiences = val
                break

        if not experiences:
            # Fall back to profile years if no history detail is available
            return ExperienceFeatureResult(
                total_experience=direct_total_years,
                ai_experience=0.0,
                product_company_experience=0.0,
                production_ml_experience=0.0,
                retrieval_experience=0.0,
                ranking_experience=0.0,
                recommendation_experience=0.0
            )

        # Initialize lists of intervals for each sub-category
        total_intervals: List[Tuple[date, date]] = []
        ai_intervals: List[Tuple[date, date]] = []
        prod_intervals: List[Tuple[date, date]] = []
        product_company_intervals: List[Tuple[date, date]] = []
        retrieval_intervals: List[Tuple[date, date]] = []
        ranking_intervals: List[Tuple[date, date]] = []
        rec_intervals: List[Tuple[date, date]] = []

        for exp in experiences:
            if not isinstance(exp, dict):
                continue

            # Parse start and end dates
            start_str = exp.get("start_date") or exp.get("from_date")
            end_str = exp.get("end_date") or exp.get("to_date")
            
            start_date = self._parse_date(start_str)
            if not start_date:
                continue

            end_date = self._parse_date(end_str)
            if not end_date:
                # If marked is_current or missing end date, default to today
                if exp.get("is_current") or not end_str:
                    end_date = date.today()
                else:
                    end_date = start_date

            if start_date > end_date:
                start_date, end_date = end_date, start_date

            interval = (start_date, end_date)
            total_intervals.append(interval)

            # Extract fields for text matching
            title = str(exp.get("title") or "").lower()
            description = str(exp.get("description") or "").lower()
            company = str(exp.get("company") or "").lower()
            combined_text = f"{title} {description}"

            # 1. AI Experience
            if self.ai_regex.search(combined_text):
                ai_intervals.append(interval)

            # 2. Product Company Experience
            if any(pc in company for pc in self.product_companies):
                product_company_intervals.append(interval)

            # 3. Production ML Experience
            if self.production_ml_regex.search(combined_text):
                prod_intervals.append(interval)

            # 4. Retrieval Experience
            if self.retrieval_regex.search(combined_text):
                retrieval_intervals.append(interval)

            # 5. Ranking Experience
            if self.ranking_regex.search(combined_text):
                ranking_intervals.append(interval)

            # 6. Recommendation Experience
            if self.recommendation_regex.search(combined_text):
                rec_intervals.append(interval)

        # Merge all intervals
        total_exp = self._merge_intervals(total_intervals)
        # Use direct years if detail calculation yields zero but direct field is set
        if total_exp == 0.0 and direct_total_years > 0.0:
            total_exp = direct_total_years

        return ExperienceFeatureResult(
            total_experience=total_exp,
            ai_experience=self._merge_intervals(ai_intervals),
            product_company_experience=self._merge_intervals(product_company_intervals),
            production_ml_experience=self._merge_intervals(prod_intervals),
            retrieval_experience=self._merge_intervals(retrieval_intervals),
            ranking_experience=self._merge_intervals(ranking_intervals),
            recommendation_experience=self._merge_intervals(rec_intervals)
        )
