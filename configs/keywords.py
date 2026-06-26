"""Keyword groups and unrelated domains configuration for Stage-1 retrieval."""

from typing import List, Set

# GROUP A (Highest Priority)
KEYWORDS_GROUP_A: List[str] = [
    "retrieval",
    "ranking",
    "matching",
    "search",
    "embeddings",
    "embedding",
    "vector",
    "python"
]

# GROUP B
KEYWORDS_GROUP_B: List[str] = [
    "faiss",
    "milvus",
    "pinecone",
    "qdrant",
    "weaviate",
    "elasticsearch",
    "opensearch"
]

# GROUP C
KEYWORDS_GROUP_C: List[str] = [
    "rag",
    "reranking",
    "sentence-transformers",
    "bge",
    "e5",
    "hybrid retrieval",
    "semantic search"
]

# GROUP D
KEYWORDS_GROUP_D: List[str] = [
    "ndcg",
    "mrr",
    "map",
    "ab testing",
    "offline evaluation",
    "online evaluation"
]

# Unrelated domain titles for Condition A
UNRELATED_TITLES: List[str] = [
    "marketing manager",
    "hr manager",
    "accountant",
    "civil engineer",
    "mechanical engineer",
    "customer support",
    "operations manager"
]

# Relevance keywords for Condition B (union of all target keywords)
RELEVANCE_KEYWORDS: Set[str] = set(
    KEYWORDS_GROUP_A + KEYWORDS_GROUP_B + KEYWORDS_GROUP_C + KEYWORDS_GROUP_D
)
