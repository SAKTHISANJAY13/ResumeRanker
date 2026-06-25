"""Tests for the candidate loader module."""

import gzip
import os
import tempfile
import pytest
import orjson
from src.stage1.candidate_loader import load_candidates

def test_load_candidates_valid():
    """Tests loading candidates from a valid gzipped JSONL file."""
    candidates_data = [
        {"candidate_id": "cand_001", "name": "Alice"},
        {"candidate_id": "cand_002", "name": "Bob"}
    ]
    
    with tempfile.NamedTemporaryFile(suffix=".jsonl.gz", delete=False) as tf:
        temp_path = tf.name
        
    try:
        with gzip.open(temp_path, "wb") as f:
            for c in candidates_data:
                f.write(orjson.dumps(c) + b"\n")
                
        loaded = list(load_candidates(temp_path))
        assert len(loaded) == 2
        assert loaded[0]["candidate_id"] == "cand_001"
        assert loaded[1]["name"] == "Bob"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_load_candidates_with_corrupted_lines():
    """Tests that corrupted JSON lines are safely skipped and do not crash load."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl.gz", delete=False) as tf:
        temp_path = tf.name
        
    try:
        with gzip.open(temp_path, "wb") as f:
            f.write(orjson.dumps({"candidate_id": "cand_001"}) + b"\n")
            f.write(b"this is invalid json content\n")
            f.write(orjson.dumps({"candidate_id": "cand_002"}) + b"\n")
            
        loaded = list(load_candidates(temp_path))
        # Invalid line should be skipped
        assert len(loaded) == 2
        assert loaded[0]["candidate_id"] == "cand_001"
        assert loaded[1]["candidate_id"] == "cand_002"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_load_candidates_file_not_found():
    """Tests loader behavior when file is missing."""
    with pytest.raises(FileNotFoundError):
        list(load_candidates("non_existent_file.jsonl.gz"))

def test_load_candidates_uncompressed():
    """Tests loading candidates from an uncompressed (raw) JSONL file."""
    candidates_data = [
        {"candidate_id": "cand_101", "name": "Charlie"},
        {"candidate_id": "cand_102", "name": "Diana"}
    ]
    
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tf:
        temp_path = tf.name
        
    try:
        with open(temp_path, "wb") as f:
            for c in candidates_data:
                f.write(orjson.dumps(c) + b"\n")
                
        loaded = list(load_candidates(temp_path))
        assert len(loaded) == 2
        assert loaded[0]["candidate_id"] == "cand_101"
        assert loaded[1]["name"] == "Diana"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
