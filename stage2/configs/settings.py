\"\"\"Configuration settings for Stage-2 Reranking Pipeline.\"\"\"

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Stage2Settings:
    \"\"\"Settings and constraints for the Stage-2 candidate reranking (20k -> 5k).\"\"\"
    
    # Paths
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    INPUT_STAGE1_CSV: str = os.path.join(PROJECT_ROOT, "data", "outputs", "stage1_top20k.csv")
    OUTPUT_STAGE2_CSV: str = os.path.join(PROJECT_ROOT, "data", "outputs", "stage2_top5k.csv")
    RAW_CANDIDATES_GZ: str = os.path.join(PROJECT_ROOT, "data", "candidates.jsonl.gz")
    
    # Reranking Parameters
    STAGE1_INPUT_SIZE: int = 20000
    STAGE2_OUTPUT_SIZE: int = 5000
    
    # Execution & Performance
    CPU_CORES_LIMIT: int = 4          # Number of processes/threads to use for feature engineering
    BATCH_SIZE: int = 1000            # Chunk size for parallel batch processing to limit peak memory
    
    # File Encoding
    ENCODING: str = "utf-8"

# Instantiate settings configuration
settings = Stage2Settings()
