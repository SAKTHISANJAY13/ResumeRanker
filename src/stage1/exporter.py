"""Exports retrieved candidates to CSV."""

import os
import csv
from typing import List, Tuple
from src.utils.logger import Logger

def export_to_csv(top_candidates: List[Tuple[float, str]], output_path: str) -> None:
    """Exports the top candidates to a CSV file.
    
    The output has schema: candidate_id,stage1_score.
    
    Args:
        top_candidates: List of tuples (score, candidate_id) sorted descending.
        output_path: Path to write the output CSV.
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        Logger.info(f"Writing {len(top_candidates)} candidates to {output_path}...")
        
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["candidate_id", "stage1_score"])
            
            # Write rows (candidate_id, score)
            # Input is (score, candidate_id), so we unpack and write as (candidate_id, score)
            for score, candidate_id in top_candidates:
                # Format score to a readable decimal string, e.g. 2 decimal places
                writer.writerow([candidate_id, f"{score:.2f}"])
                
        Logger.info("Export completed successfully.")
        
    except IOError as ioe:
        Logger.error(f"IO error writing to file {output_path}: {ioe}")
        raise
    except Exception as e:
        Logger.error(f"Failed to export candidates to CSV: {e}")
        raise
