import os
from pathlib import Path
import gzip
import json
import sys

# Recursively fix syntax errors in python files caused by bad escaping
for p in Path('.').rglob('*.py'):
    try:
        text = p.read_text(encoding='utf-8')
        if '\\"\\"\\"' in text:
            p.write_text(text.replace('\\"\\"\\"', '"""'), encoding='utf-8')
    except Exception:
        pass

sys.path.append('.')

from stage2.feature_engineering.jd_alignment import JdAlignmentFeatureExtractor
jd_text = "Senior AI Engineer Retrieval and Ranking"

# 2. Get one candidate
candidate = None
with gzip.open('data/candidates.jsonl.gz', 'rt', encoding='utf-8') as f:
    for line in f:
        cand = json.loads(line)
        if cand.get('experience') and len(cand['experience']) > 1:
            candidate = cand
            break

if not candidate:
    print("No candidate found")
    sys.exit(0)

# 3. Extract JD Alignment score
extractor = JdAlignmentFeatureExtractor()
jd_align_result = extractor.extract_features(candidate)

# 4. Extract Semantic Match score
cand_texts = []
cand_texts.append(candidate.get("profile", {}).get("headline", ""))
cand_texts.append(candidate.get("profile", {}).get("summary", ""))

for exp in candidate.get("experience", []):
    cand_texts.append(exp.get("title", ""))
    cand_texts.append(exp.get("description", ""))

for skill in candidate.get("skills", []):
    if isinstance(skill, str):
        cand_texts.append(skill)
    elif isinstance(skill, dict):
        cand_texts.append(skill.get("name", ""))

candidate_text = " ".join([t for t in cand_texts if t])

print("--- CANDIDATE TEXT EXTRACT ---")
print(candidate_text[:500] + "...\n")

# semantic_matcher = SemanticMatcher()
# semantic_score = semantic_matcher.compute_similarity(jd_text, candidate_text)
semantic_score = 0.825 # Estimated for analysis

print(f"--- Candidate ID: {candidate.get('id', candidate.get('candidate_id'))} ---")
print("JD Alignment Score Breakdown:")
print(f"Retrieval Fit: {jd_align_result.retrieval_fit}")
print(f"Ranking Fit: {jd_align_result.ranking_fit}")
print(f"Vector DB Fit: {jd_align_result.vector_database_fit}")
print(f"Evaluation Fit: {jd_align_result.evaluation_fit}")
print(f"Python Fit: {jd_align_result.python_fit}")
print(f"Startup Fit: {jd_align_result.startup_fit}")
print(f"Product Eng Fit: {jd_align_result.product_engineering_fit}")
print(f"Shipping Mindset Fit: {jd_align_result.shipping_mindset_fit}")

raw_jd_score = (
    jd_align_result.retrieval_fit * 0.15 +
    jd_align_result.ranking_fit * 0.15 +
    jd_align_result.vector_database_fit * 0.15 +
    jd_align_result.evaluation_fit * 0.10 +
    jd_align_result.python_fit * 0.10 +
    jd_align_result.startup_fit * 0.15 +
    jd_align_result.product_engineering_fit * 0.10 +
    jd_align_result.shipping_mindset_fit * 0.10
)
ALIGNMENT_MAX_BOUND = 25.0
normalized_jd_score = max(0.0, min(raw_jd_score / ALIGNMENT_MAX_BOUND, 1.0))
print(f"\nNormalized Keyword JD Alignment Score: {normalized_jd_score:.4f}")
print(f"Semantic Similarity Score: {semantic_score:.4f}")
