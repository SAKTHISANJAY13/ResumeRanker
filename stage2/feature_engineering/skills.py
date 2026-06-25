\"\"\"Skills feature engineering module for Stage-2 reranking.\"\"\"

import re
from dataclasses import dataclass
from typing import List, Dict, Set, Any, Optional
from src.utils.logger import Logger

# Try importing the Stage-2 configurations; fall back to defaults if not yet generated
try:
    from stage2.configs.keywords import (
        REQUIRED_SKILLS,
        PREFERRED_SKILLS,
        BONUS_SKILLS,
        PENALTY_SKILLS,
        ALIAS_MAP
    )
except ImportError:
    # Production-grade fallback constants for a Senior AI Engineer role
    REQUIRED_SKILLS = ["python", "ml", "dl", "nlp", "retrieval", "ranking"]
    PREFERRED_SKILLS = [
        "llm", "genai", "rag", "vector database", "faiss", 
        "milvus", "pinecone", "qdrant", "weaviate"
    ]
    BONUS_SKILLS = ["pytorch", "tensorflow", "k8s", "mlops", "system design"]
    PENALTY_SKILLS = ["marketing", "sales", "hr", "recruitment", "finance", "accounting"]
    
    # Mapping of various spelling / acronyms to canonical representations
    ALIAS_MAP = {
        "large language models": "llm",
        "large language model": "llm",
        "llms": "llm",
        "generative ai": "genai",
        "genai": "genai",
        "gen-ai": "genai",
        "gen ai": "genai",
        "machine learning": "ml",
        "deep learning": "dl",
        "natural language processing": "nlp",
        "information retrieval": "retrieval",
        "recommender systems": "recsys",
        "recommendation systems": "recsys",
        "rec sys": "recsys",
        "recsys": "recsys",
        "kubernetes": "k8s",
        "k8s": "k8s",
        "artificial intelligence": "ai",
        "neural networks": "neural network",
        "neural networks (dl)": "neural network"
    }

@dataclass(frozen=True)
class SkillsFeatureResult:
    \"\"\"Advanced skills features computed for a candidate profile.\"\"\"
    required_matched_count: int
    required_coverage_ratio: float
    preferred_matched_count: int
    preferred_coverage_ratio: float
    bonus_matched_count: int
    penalty_matched_count: int
    total_skills_count: int


class SkillsFeatureExtractor:
    \"\"\"Normalizes and groups candidate skills into semantic buckets.\"\"\"

    def __init__(self) -> None:
        # Lowercase the config groups for safe matching
        self.alias_map = {k.lower().strip(): v.lower().strip() for k, v in ALIAS_MAP.items()}
        self.required_skills = {s.lower().strip() for s in REQUIRED_SKILLS}
        self.preferred_skills = {s.lower().strip() for s in PREFERRED_SKILLS}
        self.bonus_skills = {s.lower().strip() for s in BONUS_SKILLS}
        self.penalty_skills = {s.lower().strip() for s in PENALTY_SKILLS}

    def _normalize(self, skill_name: str) -> str:
        \"\"\"Normalizes white space and maps skill aliases to canonical terms.\"\"\"
        if not skill_name:
            return ""
        # Convert to lowercase and clean punctuation except characters like +, # (C++, C#)
        clean = skill_name.strip().lower()
        clean = re.sub(r"[^\w\s\-\+\#]", "", clean)
        clean = " ".join(clean.split())
        
        # Return mapped alias or the normalized original
        return self.alias_map.get(clean, clean)

    def extract_features(self, candidate: Dict[str, Any]) -> SkillsFeatureResult:
        \"\"\"Extracts and categorizes skills features for a single candidate profile.\"\"\"
        candidate_id = candidate.get("candidate_id") or candidate.get("id") or "UNKNOWN"
        Logger.info(f"Extracting skills features for candidate {candidate_id}")

        # Locate candidate skills list
        skills = candidate.get("skills")
        if not isinstance(skills, list):
            skills = []

        # Extract and normalize skills
        normalized_candidate_skills: Set[str] = set()
        for item in skills:
            if isinstance(item, str):
                normalized = self._normalize(item)
                if normalized:
                    normalized_candidate_skills.add(normalized)
            elif isinstance(item, dict):
                name = item.get("name") or item.get("title") or item.get("skill_name")
                if name and isinstance(name, str):
                    normalized = self._normalize(name)
                    if normalized:
                        normalized_candidate_skills.add(normalized)

        # Match against our configuration buckets
        req_matches = normalized_candidate_skills.intersection(self.required_skills)
        pref_matches = normalized_candidate_skills.intersection(self.preferred_skills)
        bonus_matches = normalized_candidate_skills.intersection(self.bonus_skills)
        penalty_matches = normalized_candidate_skills.intersection(self.penalty_skills)

        # Calculate ratios (handling empty sets safely)
        req_ratio = len(req_matches) / len(self.required_skills) if self.required_skills else 0.0
        pref_ratio = len(pref_matches) / len(self.preferred_skills) if self.preferred_skills else 0.0

        return SkillsFeatureResult(
            required_matched_count=len(req_matches),
            required_coverage_ratio=req_ratio,
            preferred_matched_count=len(pref_matches),
            preferred_coverage_ratio=pref_ratio,
            bonus_matched_count=len(bonus_matches),
            penalty_matched_count=len(penalty_matches),
            total_skills_count=len(normalized_candidate_skills)
        )
