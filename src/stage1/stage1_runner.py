"""Orchestrates the Stage-1 candidate retrieval pipeline."""

import time
from typing import Dict, Any, List
from configs import settings, keywords, weights
from src.stage1.candidate_loader import load_candidates
from src.stage1.text_builder import build_searchable_text
from src.stage1.title_matcher import TitleMatcher
from src.stage1.keyword_matcher import KeywordMatcher
from src.stage1.experience_scorer import ExperienceScorer
from src.stage1.filters import should_reject
from src.stage1.scorer import (
    CandidateScorer,
    TitleScorerComponent,
    KeywordScorerComponent,
    ExperienceScorerComponent
)
from src.stage1.heap_manager import HeapManager
from src.stage1.exporter import export_to_csv
from src.utils.logger import Logger
from src.utils.timer import Timer

def run_stage1(
    data_path: str = settings.DEFAULT_DATA_PATH,
    output_path: str = settings.DEFAULT_OUTPUT_PATH,
    k: int = settings.TOP_K
) -> None:
    """Runs the Stage-1 candidate retrieval pipeline.
    
    Streams candidates, builds searchable texts, filters out obviously
    irrelevant candidates, scores the remainder, tracks the top K candidates
    using a min-heap, and exports them to a CSV file.
    
    Args:
        data_path: Path to the gzipped candidates dataset.
        output_path: Path to write the output CSV.
        k: Number of candidates to retain (default: 20,000).
    """
    Logger.info("Initializing Stage-1 Retrieval Pipeline components...")
    
    # 1. Initialize matchers and scorer components
    title_matcher = TitleMatcher(weights.TITLE_BOOSTS)
    
    # Map keyword groups dynamically from keywords config
    keyword_groups = {
        "GROUP_A": keywords.KEYWORDS_GROUP_A,
        "GROUP_B": keywords.KEYWORDS_GROUP_B,
        "GROUP_C": keywords.KEYWORDS_GROUP_C,
        "GROUP_D": keywords.KEYWORDS_GROUP_D
    }
    keyword_matcher = KeywordMatcher(
        keyword_groups=keyword_groups,
        group_weights=weights.KEYWORD_GROUP_WEIGHTS,
        relevance_keywords=keywords.RELEVANCE_KEYWORDS
    )
    
    experience_scorer = ExperienceScorer(weights.EXPERIENCE_SCORES)
    
    # Register scoring components
    components = [
        TitleScorerComponent(title_matcher),
        KeywordScorerComponent(keyword_matcher),
        ExperienceScorerComponent(experience_scorer)
    ]
    scorer = CandidateScorer(components)
    
    # Initialize Heap Manager
    heap_manager = HeapManager(k)
    
    processed_count = 0
    rejected_count = 0
    retained_count = 0
    
    Logger.info(f"Streaming and processing candidates from {data_path}...")
    
    with Timer() as timer:
        # Stream candidates one by one
        for candidate in load_candidates(data_path):
            processed_count += 1
            
            # Extract candidate ID (handle fallback keys safely)
            candidate_id = candidate.get("candidate_id") or candidate.get("id")
            if not candidate_id:
                Logger.warning(f"Candidate record at stream position {processed_count} lacks 'candidate_id' or 'id'. Skipping.")
                continue
                
            candidate_id = str(candidate_id)
            
            # Build normalized text representation
            searchable_text = build_searchable_text(candidate)
            
            # Apply high-recall rejection filter
            is_rejected = should_reject(
                candidate=candidate,
                searchable_text=searchable_text,
                unrelated_titles=keywords.UNRELATED_TITLES,
                has_relevance_keywords_fn=keyword_matcher.has_relevance_keywords
            )
            
            if is_rejected:
                rejected_count += 1
                continue
                
            retained_count += 1
            
            # Score candidate and retrieve final score
            score, _ = scorer.score_candidate(candidate, searchable_text)
            
            # Maintain top K in memory stream
            heap_manager.push(score, candidate_id)
            
            # Log progress every 10,000 candidates
            if processed_count % 10000 == 0:
                Logger.info(f"Progress: Processed={processed_count}, Rejected={rejected_count}, Retained={retained_count}, HeapSize={len(heap_manager)}")

    # 2. Extract and sort top candidates
    top_candidates = heap_manager.get_top_k()
    
    # 3. Export to CSV
    export_to_csv(top_candidates, output_path)
    
    # 4. Display performance metrics and execution stats
    elapsed_time = timer.elapsed
    peak_memory = Logger.get_peak_memory_mb()
    
    Logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    Logger.info("STAGE-1 PIPELINE EXECUTION SUMMARY")
    Logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    Logger.info(f"Candidates Processed : {processed_count:,}")
    Logger.info(f"Candidates Rejected  : {rejected_count:,}")
    Logger.info(f"Candidates Retained  : {retained_count:,}")
    Logger.info(f"Top-K Size (Exported): {len(top_candidates):,}")
    Logger.info(f"Elapsed Time         : {elapsed_time:.3f} seconds")
    Logger.info(f"Peak Memory Usage    : {peak_memory:.2f} MB")
    Logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
