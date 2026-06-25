"""Configuration settings for the Redrob Candidate Retrieval Pipeline."""

import os

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "candidates.jsonl.gz")
DEFAULT_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "outputs", "stage1_top20k.csv")

# Pipeline settings
TOP_K = 20000
