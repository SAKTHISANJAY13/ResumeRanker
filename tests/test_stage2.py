"""Unit and integration tests for Stage-2 Reranking Pipeline."""

import os
import csv
import gzip
import tempfile
import pytest
import orjson
from typing import Dict, Any

from stage2.feature_engineering.experience import ExperienceFeatureExtractor
from stage2.feature_engineering.skills import SkillsFeatureExtractor
from stage2.feature_engineering.behavioral import BehavioralFeatureExtractor
from stage2.feature_engineering.location import LocationFeatureExtractor
from stage2.feature_engineering.jd_alignment import JdAlignmentFeatureExtractor
from stage2.feature_engineering.anomaly import AnomalyDetector
from stage2.scoring.weighted_score import WeightedScorer
from stage2.ranking.reranker import Reranker
from stage2.explainability.feature_breakdown import generate_reasoning
from stage2.exporter import export_stage2_to_csv
from src.common.score import CandidateScore, ComponentScores

try:
    from stage2.semantic.semantic_matcher import SemanticMatcher
    HAS_SEMANTIC_DEPENDENCIES = True
except ImportError:
    HAS_SEMANTIC_DEPENDENCIES = False

@pytest.fixture
def mock_candidate() -> Dict[str, Any]:
    """Generates a realistic mock candidate for feature extraction testing."""
    return {
        "candidate_id": "CAND_0000001",
        "profile": {
            "headline": "Senior AI Engineer specializing in Search & Retrieval",
            "summary": "Experienced ML Engineer building scalable dense retrieval pipelines with Python.",
            "location": "Bangalore, India",
            "country": "India",
            "years_of_experience": 6.5,
            "current_title": "Senior AI Engineer",
            "current_company": "Google",
            "current_company_size": "10001+",
            "current_industry": "Technology"
        },
        "skills": [
            "Python",
            "Machine Learning",
            "Deep Learning",
            "Retrieval",
            {"name": "search systems"},
            {"name": "ranking"},
            "PyTorch",
            "milvus",
            "qdrant"
        ],
        "experience": [
            {
                "title": "Senior AI Engineer",
                "company": "Google",
                "start_date": "2022-01-01",
                "end_date": "Present",
                "is_current": True,
                "duration_months": 54,
                "company_size": "10001+",
                "description": "Led development of vector search using Milvus, Qdrant, and hybrid retrieval."
            },
            {
                "title": "AI Engineer",
                "company": "Startup Inc",
                "start_date": "2019-06-01",
                "end_date": "2021-12-31",
                "is_current": False,
                "duration_months": 31,
                "company_size": "11-50",
                "description": "Shipped machine learning ranking models for search, optimized inference latency."
            }
        ],
        "redrob_signals": {
            "profile_completeness_score": 95.0,
            "signup_date": "2019-01-01",
            "last_active_date": "2026-06-25",
            "open_to_work_flag": True,
            "profile_views_received_30d": 80,
            "applications_submitted_30d": 5,
            "recruiter_response_rate": 0.85,
            "avg_response_time_hours": 2.0,
            "skill_assessment_scores": {"Python": 90.0},
            "connection_count": 500,
            "endorsements_received": 45,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min_lpa": 30.0, "max_lpa": 45.0},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "github_activity_score": 75.0,
            "search_appearance_30d": 120,
            "saved_by_recruiters_30d": 8,
            "interview_completion_rate": 0.90,
            "offer_acceptance_rate": 0.80,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True
        }
    }

def test_experience_extractor(mock_candidate):
    """Tests ExperienceFeatureExtractor calculation of years and domains."""
    extractor = ExperienceFeatureExtractor()
    res = extractor.extract_features(mock_candidate)
    
    assert res.total_experience >= 6.5
    assert res.ai_experience > 0.0
    assert res.product_company_experience > 0.0
    assert res.retrieval_experience > 0.0
    assert res.ranking_experience > 0.0

def test_skills_extractor(mock_candidate):
    """Tests SkillsFeatureExtractor matching and ratios."""
    extractor = SkillsFeatureExtractor()
    res = extractor.extract_features(mock_candidate)
    
    assert res.required_matched_count >= 3
    assert res.required_coverage_ratio > 0.0
    assert res.preferred_matched_count >= 2
    assert res.bonus_matched_count >= 1
    assert res.penalty_matched_count == 0

def test_behavioral_extractor(mock_candidate):
    """Tests BehavioralFeatureExtractor normalization calculations."""
    extractor = BehavioralFeatureExtractor()
    res = extractor.extract_features(mock_candidate)
    
    assert 0.0 <= res.last_active_score <= 1.0
    assert 0.0 <= res.github_score <= 1.0
    assert 0.0 <= res.notice_period_score <= 1.0
    assert 0.0 <= res.overall_behavioral_score <= 1.0

def test_location_extractor(mock_candidate):
    """Tests LocationFeatureExtractor proximity and mode matching."""
    extractor = LocationFeatureExtractor()
    res = extractor.extract_features(mock_candidate)
    
    assert res.preferred_city_score == 1.0  # Bangalore
    assert res.relocation_score == 1.0      # Willing and local
    assert res.hybrid_preference_score == 1.0
    assert res.overall_location_score > 0.0

def test_jd_alignment_extractor(mock_candidate):
    """Tests JdAlignmentFeatureExtractor matching across JD pillars."""
    extractor = JdAlignmentFeatureExtractor()
    res = extractor.extract_features(mock_candidate)
    
    assert res.retrieval_fit > 0.0
    assert res.ranking_fit > 0.0
    assert res.vector_database_fit > 0.0
    assert res.python_fit > 0.0

def test_anomaly_detector_no_anomalies(mock_candidate):
    """Tests AnomalyDetector on a clean candidate with no anomalies."""
    detector = AnomalyDetector()
    res = detector.extract_features(mock_candidate)
    
    assert res.penalty_score == 0.0
    assert len(res.evidence) == 0

def test_anomaly_detector_edge_cases():
    """Tests AnomalyDetector with overlapping jobs and fake experience."""
    detector = AnomalyDetector()
    bad_cand = {
        "candidate_id": "CAND_0000002",
        "years_of_experience": 25.0,  # Unrealistic claimed span
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Company A",
                "start_date": "2020-01-01",
                "end_date": "2021-06-01",  # Overlaps with Company B
                "duration_months": 17,
                "description": "Timeline test description"
            },
            {
                "title": "Lead Engineer",
                "company": "Company B",
                "start_date": "2020-06-01",
                "end_date": "2021-12-31",
                "duration_months": 18,
                "description": "Timeline test description" # Duplicate description check
            }
        ]
    }
    res = detector.extract_features(bad_cand)
    assert res.penalty_score > 0.0
    assert len(res.evidence) > 0

def test_weighted_scorer(mock_candidate):
    """Tests WeightedScorer combination logic and anomaly decay."""
    scorer = WeightedScorer()
    
    exp_res = ExperienceFeatureExtractor().extract_features(mock_candidate)
    skills_res = SkillsFeatureExtractor().extract_features(mock_candidate)
    align_res = JdAlignmentFeatureExtractor().extract_features(mock_candidate)
    behavior_res = BehavioralFeatureExtractor().extract_features(mock_candidate)
    location_res = LocationFeatureExtractor().extract_features(mock_candidate)
    anomaly_res = AnomalyDetector().extract_features(mock_candidate)
    
    score_obj = scorer.compute_candidate_score(
        candidate_id="CAND_0000001",
        exp=exp_res,
        skills=skills_res,
        align=align_res,
        behavior=behavior_res,
        location=location_res,
        anomaly=anomaly_res,
        semantic_score=0.85
    )
    
    assert 0.0 <= score_obj.final_score <= 1.0
    assert score_obj.component_scores.experience_score > 0.0
    assert score_obj.component_scores.skills_score > 0.0
    assert score_obj.component_scores.anomaly_penalty == 0.0

def test_reranker_and_tie_breaker():
    """Tests Reranker sorting and stable tie-breaking order."""
    c1 = CandidateScore("C1", 0.85, ComponentScores(behavioral_score=0.9, experience_score=0.8))
    c2 = CandidateScore("C2", 0.85, ComponentScores(behavioral_score=0.8, experience_score=0.9)) # Tie in score
    c3 = CandidateScore("C3", 0.90, ComponentScores()) # Highest score
    
    candidates = [c1, c2, c3]
    ranked = Reranker.rerank(candidates, top_k=3)
    
    assert len(ranked) == 3
    assert ranked[0].candidate_id == "C3" # Highest score first
    assert ranked[1].candidate_id == "C1" # Breaks tie using higher behavioral score (0.9 vs 0.8)
    assert ranked[2].candidate_id == "C2"
    assert ranked[0].rank == 1
    assert ranked[1].rank == 2
    assert ranked[2].rank == 3

def test_explainability_reasoning():
    """Tests generate_reasoning output correctness."""
    features = {
        "experience": 0.80,
        "skills": 0.90,
        "semantic": 0.85,
        "behavior": 0.75,
        "penalty": 0.0
    }
    reason = generate_reasoning(features, 0.84)
    assert "Demonstrates" in reason
    assert "0.90" in reason
    assert "0.85" in reason
    assert "Calibrated score: 0.84" in reason

@pytest.mark.skipif(not HAS_SEMANTIC_DEPENDENCIES, reason="Requires sentence-transformers and torch")
def test_semantic_matcher():
    """Tests SemanticMatcher embedding similarity calculation."""
    matcher = SemanticMatcher()
    jd = "Senior AI Engineer Retrieval and Ranking"
    cand_text = "I am a Senior AI Engineer specializing in semantic search and vector databases."
    
    score = matcher.compute_similarity(jd, cand_text)
    assert 0.0 <= score <= 1.0
    
    batch_scores = matcher.batch_compute_similarity(jd, [cand_text, ""])
    assert len(batch_scores) == 2
    assert batch_scores[1] == 0.0

def test_exporter():
    """Tests export_stage2_to_csv schema output validation."""
    c1 = CandidateScore("CAND_0000001", 0.85, ComponentScores(experience_score=0.8, skills_score=0.9), reasoning="Top candidate")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_output.csv")
        export_stage2_to_csv([c1], csv_path)
        
        assert os.path.exists(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header[0] == "candidate_id"
            assert header[1] == "rank"
            assert header[2] == "score"
            assert header[3] == "reasoning"
            assert len(header) == 11
            
            row = next(reader)
            assert row[0] == "CAND_0000001"
            assert row[2] == "0.8500"
            assert row[3] == "Top candidate"

def test_pipeline_integration(mock_candidate):
    """Integration test running stage2 pipeline end-to-end using temp mock files."""
    from stage2.pipeline import run_stage2_pipeline
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Create mock Stage-1 CSV
        csv_path = os.path.join(tmpdir, "stage1_top20k.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["candidate_id", "stage1_score"])
            writer.writerow(["CAND_0000001", "15.5"])
            
        # 2. Create mock Gzipped JSONL raw candidate profiles
        gz_path = os.path.join(tmpdir, "candidates.jsonl.gz")
        with gzip.open(gz_path, "wb") as f:
            line = orjson.dumps(mock_candidate) + b"\n"
            f.write(line)
            
        # Run pipeline (bypass semantic by mock environment or catch missing warning)
        ranked = run_stage2_pipeline(
            stage1_csv_path=csv_path,
            raw_data_path=gz_path,
            top_k=1
        )
        
        # Verify execution
        assert len(ranked) == 1
        assert ranked[0].candidate_id == "CAND_0000001"
        assert ranked[0].rank == 1
        assert ranked[0].final_score > 0.0
        assert len(ranked[0].reasoning) > 0
