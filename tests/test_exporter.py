"""Tests for the exporter module."""

import os
import tempfile
import csv
from src.stage1.exporter import export_to_csv

def test_exporter_writes_csv():
    """Tests that export_to_csv creates the file with correct headers and formatting."""
    top_candidates = [
        (15.234, "cand_001"),
        (8.5, "cand_002")
    ]
    
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
        temp_path = tf.name
        
    try:
        export_to_csv(top_candidates, temp_path)
        
        assert os.path.exists(temp_path)
        
        with open(temp_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            
            # Check headers
            assert reader[0] == ["candidate_id", "stage1_score"]
            
            # Check row 1
            assert reader[1][0] == "cand_001"
            assert reader[1][1] == "15.23"  # Formatted to 2 decimals
            
            # Check row 2
            assert reader[2][0] == "cand_002"
            assert reader[2][1] == "8.50"
            
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
