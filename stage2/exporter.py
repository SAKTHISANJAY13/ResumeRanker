"""Exports Stage-2 reranked candidates to CSV."""

import os
import csv
from typing import List
from src.utils.logger import Logger
from src.common.score import CandidateScore

def export_stage2_to_csv(ranked_candidates: List[CandidateScore], output_path: str) -> None:
    """Exports the ranked candidates to a CSV file.
    
    The output contains candidate_id, rank, score, reasoning, and individual
    component scores for transparency and explainability.
    
    Args:
        ranked_candidates: List of CandidateScore objects sorted by rank.
        output_path: Path to write the output CSV.
    """
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        Logger.info(f"Writing {len(ranked_candidates)} Stage-2 candidates to {output_path}...")
        
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                "candidate_id",
                "rank",
                "score",
                "reasoning",
                "experience_score",
                "skills_score",
                "jd_alignment_score",
                "semantic_alignment_score",
                "behavioral_score",
                "location_score",
                "anomaly_penalty"
            ])
            
            # Write rows
            for cand in ranked_candidates:
                cs = cand.component_scores
                writer.writerow([
                    cand.candidate_id,
                    cand.rank or "",
                    f"{cand.final_score:.4f}",
                    cand.reasoning or "",
                    f"{cs.experience_score:.4f}" if cs else "0.0000",
                    f"{cs.skills_score:.4f}" if cs else "0.0000",
                    f"{cs.jd_alignment_score:.4f}" if cs else "0.0000",
                    f"{cs.semantic_alignment_score:.4f}" if cs else "0.0000",
                    f"{cs.behavioral_score:.4f}" if cs else "0.0000",
                    f"{cs.location_score:.4f}" if cs else "0.0000",
                    f"{cs.anomaly_penalty:.4f}" if cs else "0.0000"
                ])
                
        Logger.info("Stage-2 export completed successfully.")
        
    except IOError as ioe:
        Logger.error(f"IO error writing to file {output_path}: {ioe}")
        raise
    except Exception as e:
        Logger.error(f"Failed to export Stage-2 candidates to CSV: {e}")
        raise
