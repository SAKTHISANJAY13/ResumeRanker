\"\"\"Stage-2 ranking pipeline orchestrator.\"\"\"

import csv
from typing import List, Set
from src.utils.logger import Logger
from src.stage1.candidate_loader import load_candidates
from src.common.score import CandidateScore
from stage2.configs.settings import settings
from stage2.feature_engineering.experience import ExperienceFeatureExtractor
from stage2.feature_engineering.skills import SkillsFeatureExtractor
from stage2.feature_engineering.behavioral import BehavioralFeatureExtractor
from stage2.feature_engineering.location import LocationFeatureExtractor
from stage2.feature_engineering.jd_alignment import JdAlignmentFeatureExtractor
from stage2.feature_engineering.anomaly import AnomalyDetector
from stage2.scoring.weighted_score import WeightedScorer
from stage2.ranking.tie_breaker import TieBreaker

def run_stage2_pipeline(
    stage1_csv_path: str = settings.INPUT_STAGE1_CSV,
    raw_data_path: str = settings.RAW_CANDIDATES_GZ,
    top_k: int = settings.STAGE2_OUTPUT_SIZE
) -> List[CandidateScore]:
    \"\"\"Runs the complete Stage-2 Reranking Pipeline.
    
    Flow:
        1. Load candidate IDs from Stage-1 retrieval.
        2. Stream candidate profiles from raw gzipped JSONL.
        3. Compute advanced features: Experience, Skills, Behavior, Location, JD Alignment, and Anomalies.
        4. Calculate final weighted scores.
        5. Sort candidate results deterministically (breaking ties stably).
        6. Retain and rank top 5000 candidates.
        
    Args:
        stage1_csv_path: Path to the Stage-1 candidate output CSV.
        raw_data_path: Path to the compressed raw candidate profiles.
        top_k: Number of candidates to select (default: 5000).
        
    Returns:
        Ranked list of CandidateScore objects.
    \"\"\"
    Logger.info("Initializing Stage-2 Reranking Pipeline components...")
    
    # 1. Load target candidate IDs from Stage-1 CSV
    target_ids: Set[str] = set()
    try:
        with open(stage1_csv_path, "r", encoding=settings.ENCODING) as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header row
            for row in reader:
                if row:
                    target_ids.add(row[0].strip())
        Logger.info(f"Loaded {len(target_ids)} target candidates from Stage-1.")
    except Exception as e:
        Logger.error(f"Failed to read Stage-1 CSV at {stage1_csv_path}: {e}")
        raise

    if not target_ids:
        Logger.warning("No target candidate IDs to process for Stage-2. Returning empty results.")
        return []

    # 2. Initialize feature extractors and scoring componentry
    exp_extractor = ExperienceFeatureExtractor()
    skills_extractor = SkillsFeatureExtractor()
    behavior_extractor = BehavioralFeatureExtractor()
    location_extractor = LocationFeatureExtractor()
    alignment_extractor = JdAlignmentFeatureExtractor()
    anomaly_detector = AnomalyDetector()
    scorer = WeightedScorer()

    candidate_scores: List[CandidateScore] = []
    processed_count = 0
    matched_count = 0

    Logger.info(f"Streaming and processing target candidate profiles from {raw_data_path}...")

    # 3. Stream raw profiles and execute features & scoring
    for candidate in load_candidates(raw_data_path):
        processed_count += 1
        
        cid = candidate.get("candidate_id") or candidate.get("id")
        if not cid:
            continue
            
        cid = str(cid)
        if cid not in target_ids:
            continue

        matched_count += 1

        # Extract features
        exp_res = exp_extractor.extract_features(candidate)
        skills_res = skills_extractor.extract_features(candidate)
        behavior_res = behavior_extractor.extract_features(candidate)
        location_res = location_extractor.extract_features(candidate)
        align_res = alignment_extractor.extract_features(candidate)
        anomaly_res = anomaly_detector.extract_features(candidate)

        # Compute candidate final score and component breakdown
        score_obj = scorer.compute_candidate_score(
            candidate_id=cid,
            exp=exp_res,
            skills=skills_res,
            align=align_res,
            behavior=behavior_res,
            location=location_res,
            anomaly=anomaly_res
        )
        candidate_scores.append(score_obj)

        if matched_count % 1000 == 0:
            Logger.info(f"Scored {matched_count} candidates out of {len(target_ids)} target profiles...")

    Logger.info(f"Completed scoring. Total matched and scored candidates: {len(candidate_scores)}")

    # 4. Deterministic and stable sorting (tie-breaking hierarchy)
    sorted_candidates = TieBreaker.sort_deterministically(candidate_scores)

    # 5. Select top K candidates and assign rank indices
    top_candidates = sorted_candidates[:top_k]
    for rank_idx, candidate in enumerate(top_candidates, 1):
        candidate.rank = rank_idx

    Logger.info(f"Stage-2 ranking completed. Returning top {len(top_candidates)} ranked candidates.")
    return top_candidates
