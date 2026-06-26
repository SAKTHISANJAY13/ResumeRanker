"""CLI entrypoint for running the Redrob Candidate Retrieval Pipeline."""

import argparse
import sys
from configs import settings
from src.stage1.stage1_runner import run_stage1
from src.utils.logger import Logger

def main() -> None:
    """CLI entrypoint to parse arguments and execute Stage-1 pipeline."""
    parser = argparse.ArgumentParser(
        description="Redrob Intelligent Candidate Discovery & Ranking Challenge - Stage 1 Retrieval Pipeline"
    )
    
    parser.add_argument(
        "--data-path", "-d",
        type=str,
        default=settings.DEFAULT_DATA_PATH,
        help=f"Path to input gzipped candidate JSONL data. (Default: {settings.DEFAULT_DATA_PATH})"
    )
    
    parser.add_argument(
        "--output-path", "-o",
        type=str,
        default=settings.DEFAULT_OUTPUT_PATH,
        help=f"Path to export retrieved candidate CSV. (Default: {settings.DEFAULT_OUTPUT_PATH})"
    )
    
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=settings.TOP_K,
        help=f"Number of top scoring candidates to retrieve. (Default: {settings.TOP_K})"
    )
    
    args = parser.parse_args()
    
    try:
        run_stage1(
            data_path=args.data_path,
            output_path=args.output_path,
            k=args.top_k
        )
    except FileNotFoundError:
        Logger.error("Pipeline aborted: Data file not found.")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Pipeline failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
