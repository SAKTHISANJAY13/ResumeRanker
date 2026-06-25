"""
Keyword configuration for Stage-2 Reranking Pipeline.

This module centralizes all keyword lists used for:
1. Skill matching and coverage scoring
2. JD alignment concept detection
3. Experience domain categorization

ORGANIZATION:
- Skill Categories: Required, Preferred, Bonus, Penalty skills
- Concept Groups: 8 dimensions matching the JD (Retrieval, Ranking, etc.)
- Aliases: Term substitutions (LLM -> Large Language Models)
- Helper Functions: Normalization and matching utilities

DESIGN PRINCIPLE:
All keywords are organized by ROLE-SPECIFIC CONCEPT rather than generic skill.
This makes it easy to swap in entirely new keyword sets for different JDs.

To adapt for a new JD:
1. Update REQUIRED_SKILLS, PREFERRED_SKILLS, etc. based on new role
2. Update each CONCEPT_WORDS group with keywords from new JD
3. Run validate_keywords() to check for issues
4. All modules automatically use updated keywords
"""

# ============================================================================
# ALIASES: Term Normalization
# ============================================================================
"""
Maps common variations to canonical terms.
Used for normalizing candidate skills before matching.

Example: "LLM" -> "large language models" (normalized to canonical form)
"""

SKILL_ALIASES = {
    # Large Language Models
    "llm": "large language models",
    "llms": "large language models",
    "gpt": "large language models",
    "gpt-3": "large language models",
    "gpt-4": "large language models",
    "openai": "large language models",
    "chatgpt": "large language models",
    "claude": "large language models",
    "anthropic": "large language models",
    "palm": "large language models",
    
    # Generative AI
    "genai": "generative ai",
    "gen ai": "generative ai",
    "generative models": "generative ai",
    "diffusion": "generative ai",
    "transformers": "generative ai",
    
    # Vector Databases & Embeddings
    "milvus": "vector database",
    "pinecone": "vector database",
    "weaviate": "vector database",
    "qdrant": "vector database",
    "faiss": "vector search",
    "embeddings": "embedding models",
    "vector embeddings": "embedding models",
    "semantic search": "retrieval",
    
    # Ranking/Information Retrieval
    "ir": "information retrieval",
    "information retrieval": "retrieval",
    "learning to rank": "ranking",
    "l2r": "ranking",
    "bm25": "ranking",
    "solr": "retrieval",
    "elasticsearch": "retrieval",
    "lucene": "retrieval",
    
    # Recommendation Systems
    "recommender": "recommendation systems",
    "recommenders": "recommendation systems",
    "collaborative filtering": "recommendation systems",
    
    # Machine Learning Infrastructure
    "ml infrastructure": "production machine learning",
    "mlops": "production machine learning",
    "ml ops": "production machine learning",
    "mlflow": "production machine learning",
    "kubeflow": "production machine learning",
    "airflow": "production machine learning",
    
    # Python Ecosystem (Language)
    "python": "python",
    "py": "python",
    
    # Evaluation & Metrics
    "metrics": "evaluation",
    "ndcg": "evaluation",
    "mrr": "evaluation",
    "precision": "evaluation",
    "recall": "evaluation",
    "auc": "evaluation",
    "roc": "evaluation",
}


# ============================================================================
# REQUIRED SKILLS: Must-Haves for Senior AI Engineer - Retrieval & Ranking Role
# ============================================================================
"""
Skills that candidates MUST have or strongly possess.
Missing required skills significantly reduces score.

For this role (Retrieval & Ranking specialist):
- Python: Core language for ML systems
- Machine Learning Fundamentals: Foundation for all work
- Retrieval/Search: Core job responsibility
- Ranking Algorithms: Core job responsibility
- Production ML: Will ship systems to production
"""

REQUIRED_SKILLS = [
    # Core Language
    "python",
    
    # Core ML Concepts
    "machine learning",
    "deep learning",
    
    # Core Job Responsibilities
    "retrieval",
    "search systems",
    "information retrieval",
    "ranking",
    "ranking algorithms",
    
    # Production Reality
    "production machine learning",
    "deploying machine learning systems",
    "ml systems",
]


# ============================================================================
# PREFERRED SKILLS: Nice-to-Haves that Strengthen Candidate Profile
# ============================================================================
"""
Skills that are valuable but not essential.
Presence of preferred skills boosts score moderately.

For this role:
- Vector Databases: Modern retrieval infrastructure
- Evaluation Metrics: Measuring ranking quality
- Large Language Models: Trendy but increasingly important
- Distributed Systems: Scaling retrieval at scale
- Product Engineering: Shipping with focus on user value
"""

PREFERRED_SKILLS = [
    # Vector Infrastructure
    "vector databases",
    "embeddings",
    "embedding models",
    "semantic search",
    
    # Modern LLM Approaches
    "large language models",
    "generative ai",
    "transformer models",
    "neural networks",
    
    # Evaluation
    "evaluation metrics",
    "metrics",
    "ndcg",
    "mrr",
    "evaluation",
    
    # Scaling & Infrastructure
    "distributed systems",
    "apache spark",
    "kubernetes",
    "cloud infrastructure",
    "aws",
    "gcp",
    
    # Recommendation Systems (related)
    "recommendation systems",
    
    # Product-focused
    "product engineering",
    "user experience",
    "ab testing",
    "experimentation",
    
    # Data
    "data engineering",
    "data pipelines",
]


# ============================================================================
# BONUS SKILLS: Impressive Add-Ons
# ============================================================================
"""
Nice-to-have skills that indicate exceptional breadth or depth.
Presence of bonus skills provides modest boost to score.

For this role:
- Academic/Research Background: PhD, papers on ranking/retrieval
- Open Source: Contributions to ranking/search systems
- Advanced Techniques: Cross-encoder models, DPR, ColBERT, etc.
"""

BONUS_SKILLS = [
    # Research/Academic
    "machine learning research",
    "published papers",
    "phd",
    "computer science research",
    
    # Advanced Retrieval Techniques
    "dense passage retrieval",
    "dpr",
    "colbert",
    "cross-encoder",
    "bi-encoder",
    
    # Advanced Ranking
    "learning to rank",
    "pointwise ranking",
    "pairwise ranking",
    "listwise ranking",
    
    # Graph/Knowledge
    "knowledge graphs",
    "graph neural networks",
    
    # Open Source
    "open source",
    "github",
    "contributions",
    
    # Advanced ML
    "reinforcement learning",
    "causal inference",
    "bayesian methods",
    
    # Specialized Infrastructure
    "faiss",
    "elasticsearch",
    "solr",
    "lucene",
    "milvus",
    "pinecone",
    "weaviate",
    "qdrant",
]


# ============================================================================
# PENALTY SKILLS: Red Flags
# ============================================================================
"""
Skills or experience that are RED FLAGS or anti-signals for this role.

For a technical RETRIEVAL & RANKING specialist role:
- Pure Management: If only managing, not hands-on coding
- Non-Technical Roles: Sales, HR, business roles
- Outdated Tech: Flash, Silverlight, legacy systems
- Data-Light Backgrounds: Front-end, design (no data exposure)
"""

PENALTY_SKILLS = [
    # Non-Technical Roles
    "sales",
    "business development",
    "account management",
    "human resources",
    "hr",
    "recruiting",
    "operations",
    
    # Pure Management (no IC contribution)
    "management",
    "manager",
    "director",
    "vp",
    "cto",
    
    # Frontend/Design (no ML/backend)
    "ui design",
    "ux design",
    "graphic design",
    "frontend development",
    "web design",
    
    # Outdated Technologies
    "flash",
    "silverlight",
    "asp.net",
    "coldfusion",
    
    # Shallow Data Exposure
    "wordpress",
    "cms",
    "content management",
]


# ============================================================================
# CONCEPT GROUPS: JD Alignment Keywords
# ============================================================================
"""
Keyword groups for detecting alignment with 8 dimensions of the job description.

Each group represents a different aspect of the Retrieval & Ranking role.
Used by JdAlignmentFeatureExtractor to score semantic fit.

DESIGN: Each group is independent and can be replaced entirely for new JDs.
Just update RETRIEVAL_CONCEPT_WORDS, RANKING_CONCEPT_WORDS, etc.
"""

# ============================================================================
# 1. RETRIEVAL: Search & Information Retrieval Concepts
# ============================================================================
"""
Keywords indicating experience with retrieval systems, search infrastructure,
and information retrieval methodologies.

Includes: semantic search, BM25, vector search, dense retrieval, sparse retrieval,
reranking, query understanding, document indexing.
"""

RETRIEVAL_CONCEPT_WORDS = [
    # Core Retrieval
    "retrieval",
    "information retrieval",
    "search",
    "semantic search",
    
    # Retrieval Methods
    "dense retrieval",
    "sparse retrieval",
    "hybrid retrieval",
    "lexical search",
    "dense passage retrieval",
    "dpr",
    "bm25",
    "tf-idf",
    
    # Retrieval Infrastructure
    "elasticsearch",
    "solr",
    "lucene",
    "query engine",
    
    # Related Concepts
    "reranking",
    "query understanding",
    "query expansion",
    "document indexing",
    "inverted index",
    
    # Vector-based Retrieval
    "vector search",
    "similarity search",
    "approximate nearest neighbor",
    "ann",
    "knn",
    "embedding-based search",
]


# ============================================================================
# 2. RANKING: Ranking Algorithm & Learning-to-Rank Concepts
# ============================================================================
"""
Keywords indicating experience with ranking systems, learning-to-rank (L2R),
ranking algorithms, and result ordering.

Includes: pointwise/pairwise/listwise ranking, NDCG, MRR, ranking loss functions,
gradient boosting for ranking, neural ranking models.
"""

RANKING_CONCEPT_WORDS = [
    # Core Ranking
    "ranking",
    "rank",
    "sorted results",
    "result ranking",
    
    # Learning-to-Rank
    "learning to rank",
    "l2r",
    "rank learning",
    
    # Ranking Approaches
    "pointwise ranking",
    "pairwise ranking",
    "listwise ranking",
    "lambdamart",
    "lambdarank",
    "gbdt",
    "gradient boosting",
    
    # Neural Ranking
    "neural ranking",
    "neural network ranking",
    "deep learning ranking",
    "cross-encoder",
    "colbert",
    
    # Ranking Metrics (overlaps with evaluation)
    "ndcg",
    "normalized discounted cumulative gain",
    "mrr",
    "mean reciprocal rank",
    "map",
    "mean average precision",
    
    # Related Concepts
    "result diversification",
    "diversity",
    "relevance",
    "relevance model",
]


# ============================================================================
# 3. VECTOR DATABASES: Embedding Storage & Vector Search Infrastructure
# ============================================================================
"""
Keywords indicating experience with vector databases, embedding management,
and modern retrieval infrastructure.

Includes: Pinecone, Milvus, Weaviate, Qdrant, FAISS, embedding models,
vector storage, similarity search at scale.
"""

VECTOR_DATABASE_CONCEPT_WORDS = [
    # Vector Database Products
    "vector database",
    "pinecone",
    "milvus",
    "weaviate",
    "qdrant",
    "faiss",
    "annoy",
    
    # Vector Operations
    "vector search",
    "approximate nearest neighbor",
    "ann",
    "similarity search",
    "cosine similarity",
    "euclidean distance",
    
    # Embeddings
    "embeddings",
    "embedding models",
    "text embeddings",
    "semantic embeddings",
    "dense representations",
    
    # Modern Retrieval
    "semantic search",
    "embedding-based retrieval",
    "dense retrieval",
    "neural retrieval",
    
    # Related Infrastructure
    "distributed vector search",
    "high-dimensional indexing",
    "vector scaling",
]


# ============================================================================
# 4. EVALUATION METRICS: Measuring Ranking Quality & Performance
# ============================================================================
"""
Keywords indicating understanding of metrics, measurement methodologies,
and evaluation frameworks.

Includes: NDCG, MRR, MAP, precision@k, recall, AUC, ROC, A/B testing,
offline evaluation, online metrics.
"""

EVALUATION_CONCEPT_WORDS = [
    # Ranking Metrics
    "ndcg",
    "normalized discounted cumulative gain",
    "mrr",
    "mean reciprocal rank",
    "map",
    "mean average precision",
    "precision@k",
    "recall@k",
    
    # Retrieval Metrics
    "recall",
    "precision",
    "f1",
    
    # Classification/General Metrics
    "auc",
    "roc",
    "roc-auc",
    "accuracy",
    
    # Evaluation Methods
    "evaluation",
    "offline evaluation",
    "online evaluation",
    "ab testing",
    "a/b testing",
    "experimentation",
    
    # Related Concepts
    "metrics",
    "performance metrics",
    "quality metrics",
    "measurement",
]


# ============================================================================
# 5. PRODUCT ENGINEERING: Shipping with Product Focus & User Value
# ============================================================================
"""
Keywords indicating product-minded engineering approach, user-focused delivery,
and shipping features end-to-end.

Includes: product engineering, user experience, feature shipping, end-to-end
delivery, user growth, business logic, product metrics, product thinking.
"""

PRODUCT_ENGINEERING_CONCEPT_WORDS = [
    # Product Delivery
    "product engineering",
    "product development",
    "feature development",
    "end-to-end",
    "shipped",
    "shipped features",
    
    # User Focus
    "user-facing",
    "user experience",
    "ux",
    "user growth",
    "user engagement",
    
    # Product Mindset
    "product thinking",
    "product sense",
    "product metrics",
    "business logic",
    "business impact",
    
    # Client/Customer
    "client-facing",
    "client development",
    "customer feedback",
    
    # Business Models
    "saas",
    "b2b",
    "b2c",
    "marketplace",
    
    # Product Processes
    "product roadmap",
    "product strategy",
    "requirements",
    "specifications",
]


# ============================================================================
# 6. STARTUP MINDSET: Startup Environment & Scale-Up Experience
# ============================================================================
"""
Keywords indicating experience in startup/scale-up environments and startup DNA.

Includes: early-stage, MVP, rapid iteration, resource constraints, versatility,
wearing multiple hats, startup culture, fast growth, founder-led, Series A/B/C.
"""

STARTUP_MINDSET_CONCEPT_WORDS = [
    # Company Stage
    "startup",
    "early-stage",
    "scale-up",
    "growth stage",
    "series a",
    "series b",
    "series c",
    "founder-led",
    
    # Startup Culture & Approach
    "startup culture",
    "fast growth",
    "rapid iteration",
    "mvp",
    "minimum viable product",
    "lean",
    
    # Startup Constraints
    "resource constraints",
    "limited resources",
    "wearing multiple hats",
    "jack of all trades",
    "versatility",
    
    # Company Size
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "small team",
    "small company",
    
    # Startup Metrics
    "growth metrics",
    "user acquisition",
    "traction",
    "unit economics",
]


# ============================================================================
# 7. SHIPPING MINDSET: Deployment, Iteration & Production Delivery
# ============================================================================
"""
Keywords indicating shipping/deployment culture, production-ready mindset,
and iterative improvement.

Includes: shipped, deployed, launched, released, production deployment,
CI/CD, continuous delivery, iteration, production-ready, reliability,
monitoring, observability.
"""

SHIPPING_MINDSET_CONCEPT_WORDS = [
    # Deployment
    "shipped",
    "deployed",
    "launched",
    "delivered",
    "released",
    "production",
    "production deployment",
    "production-ready",
    
    # Continuous Integration/Deployment
    "ci/cd",
    "continuous integration",
    "continuous delivery",
    "continuous deployment",
    "ci cd",
    
    # Iteration & Process
    "iteration",
    "iterative improvement",
    "iterative development",
    "sprint",
    "agile",
    
    # Production Excellence
    "reliability",
    "reliability engineering",
    "observability",
    "monitoring",
    "alerting",
    "logging",
    
    # Version Control & Release
    "git",
    "version control",
    "pull request",
    "code review",
    "release management",
]


# ============================================================================
# 8. PYTHON ECOSYSTEM: Python-Specific Languages, Libraries & Frameworks
# ============================================================================
"""
Keywords indicating deep Python ecosystem knowledge.

Includes: Python, NumPy, SciPy, Pandas, Scikit-Learn, PyTorch, TensorFlow,
FastAPI, Flask, Jupyter, async/await, type hints, testing frameworks.
"""

PYTHON_ECOSYSTEM_CONCEPT_WORDS = [
    # Core Python
    "python",
    "python 3",
    
    # Scientific Computing
    "numpy",
    "scipy",
    "pandas",
    "scikit-learn",
    "sklearn",
    
    # Deep Learning Frameworks
    "pytorch",
    "tensorflow",
    "keras",
    "hugging face",
    "transformers",
    
    # Web Frameworks
    "fastapi",
    "flask",
    "django",
    "wsgi",
    
    # Data Science
    "jupyter",
    "jupyter notebook",
    "ipython",
    
    # Async & Concurrency
    "async",
    "asyncio",
    "async/await",
    "threading",
    
    # Code Quality
    "type hints",
    "type checking",
    "mypy",
    "pylint",
    "pytest",
    "testing",
    "unit tests",
    
    # Python Tools
    "pip",
    "poetry",
    "virtual environment",
    "docker",
]


# ============================================================================
# PRODUCT COMPANY LIST: Companies with Strong Product/Engineering Culture
# ============================================================================
"""
Companies known for strong product engineering, ML excellence, or early-stage
growth. Experience at these companies is a positive signal for this role.

Used by ExperienceFeatureExtractor to identify "product company" experience.

Organized by tier:
- FAANG: Scale, resources, optimization challenges
- High-Growth Tech: Fast iteration, shipping culture
- AI/ML Specialists: Deep expertise in AI/ML/Infra
- Vectors/Search: Direct experience with retrieval systems
"""

PRODUCT_COMPANIES_FAANG = [
    "google",
    "meta",
    "facebook",
    "apple",
    "amazon",
    "netflix",
    "microsoft",
]

PRODUCT_COMPANIES_HIGH_GROWTH = [
    "linkedin",
    "uber",
    "lyft",
    "stripe",
    "airbnb",
    "twitter",
    "salesforce",
    "adobe",
    "atlassian",
    "spotify",
    "zoom",
    "slack",
    "figma",
    "notion",
    "discord",
]

PRODUCT_COMPANIES_AI_ML = [
    "nvidia",
    "openai",
    "anthropic",
    "mistral",
    "together",
    "stability ai",
    "hugging face",
    "databricks",
]

PRODUCT_COMPANIES_VECTORS_SEARCH = [
    "pinecone",
    "milvus",
    "weaviate",
    "qdrant",
    "vespa",
    "elasticsearch",
]

# Combined list for easy import
PRODUCT_COMPANIES = (
    PRODUCT_COMPANIES_FAANG +
    PRODUCT_COMPANIES_HIGH_GROWTH +
    PRODUCT_COMPANIES_AI_ML +
    PRODUCT_COMPANIES_VECTORS_SEARCH
)


# ============================================================================
# VALIDATION & HELPER FUNCTIONS
# ============================================================================

def validate_keywords() -> bool:
    """
    Validates keyword configuration for consistency and coverage.
    Checks for:
    - No empty lists
    - No duplicate keywords within category
    - Aliases don't point to themselves
    
    Returns:
        bool: True if all validations pass
        
    Raises:
        AssertionError: If any validation fails
    """
    # Check skill categories are non-empty
    assert len(REQUIRED_SKILLS) > 0, "REQUIRED_SKILLS cannot be empty"
    assert len(PREFERRED_SKILLS) > 0, "PREFERRED_SKILLS cannot be empty"
    assert len(BONUS_SKILLS) > 0, "BONUS_SKILLS cannot be empty"
    
    # Check for duplicates within skill categories
    all_required = set(REQUIRED_SKILLS)
    assert len(all_required) == len(REQUIRED_SKILLS), \
        f"REQUIRED_SKILLS has {len(REQUIRED_SKILLS) - len(all_required)} duplicates"
    
    all_preferred = set(PREFERRED_SKILLS)
    assert len(all_preferred) == len(PREFERRED_SKILLS), \
        f"PREFERRED_SKILLS has {len(PREFERRED_SKILLS) - len(all_preferred)} duplicates"
    
    # Check that aliases don't point to themselves
    for key, value in SKILL_ALIASES.items():
        assert key.lower() != value.lower(), \
            f"Alias '{key}' points to itself ('{value}')"
    
    # Check concept groups are non-empty
    concept_groups = [
        ("RETRIEVAL_CONCEPT_WORDS", RETRIEVAL_CONCEPT_WORDS),
        ("RANKING_CONCEPT_WORDS", RANKING_CONCEPT_WORDS),
        ("VECTOR_DATABASE_CONCEPT_WORDS", VECTOR_DATABASE_CONCEPT_WORDS),
        ("EVALUATION_CONCEPT_WORDS", EVALUATION_CONCEPT_WORDS),
        ("PRODUCT_ENGINEERING_CONCEPT_WORDS", PRODUCT_ENGINEERING_CONCEPT_WORDS),
        ("STARTUP_MINDSET_CONCEPT_WORDS", STARTUP_MINDSET_CONCEPT_WORDS),
        ("SHIPPING_MINDSET_CONCEPT_WORDS", SHIPPING_MINDSET_CONCEPT_WORDS),
        ("PYTHON_ECOSYSTEM_CONCEPT_WORDS", PYTHON_ECOSYSTEM_CONCEPT_WORDS),
    ]
    
    for name, words in concept_groups:
        assert len(words) > 0, f"{name} cannot be empty"
        unique_words = set(words)
        assert len(unique_words) == len(words), \
            f"{name} has {len(words) - len(unique_words)} duplicates"
    
    return True


def normalize_skill(skill: str) -> str:
    """
    Normalizes a skill string using alias mappings.
    
    Example:
        normalize_skill("LLM") -> "large language models"
        normalize_skill("GenAI") -> "generative ai"
    
    Args:
        skill: Raw skill string
        
    Returns:
        Normalized skill string (lowercase)
    """
    if not isinstance(skill, str):
        return ""
    
    normalized = skill.lower().strip()
    
    # Apply aliases if match found
    if normalized in SKILL_ALIASES:
        normalized = SKILL_ALIASES[normalized]
    
    return normalized


def categorize_skill(skill: str) -> str:
    """
    Categorizes a normalized skill into one of the 4 categories.
    
    Args:
        skill: Normalized skill string (lowercase)
        
    Returns:
        Category: "required", "preferred", "bonus", "penalty", or "neutral"
    """
    skill_lower = skill.lower().strip()
    
    if skill_lower in [s.lower() for s in REQUIRED_SKILLS]:
        return "required"
    elif skill_lower in [s.lower() for s in PREFERRED_SKILLS]:
        return "preferred"
    elif skill_lower in [s.lower() for s in BONUS_SKILLS]:
        return "bonus"
    elif skill_lower in [s.lower() for s in PENALTY_SKILLS]:
        return "penalty"
    else:
        return "neutral"


# ============================================================================
# AUTO-VALIDATION
# ============================================================================

# Run validation on module import to catch configuration errors early
try:
    validate_keywords()
except AssertionError as e:
    raise AssertionError(f"Keyword validation failed: {e}")


# ============================================================================
# TUNING GUIDELINES FOR NEW JDs
# ============================================================================
"""
To adapt this configuration for a different role:

1. SKILL CATEGORIES:
   - Replace REQUIRED_SKILLS with must-have skills for new role
   - Update PREFERRED_SKILLS with valuable but non-essential skills
   - Update BONUS_SKILLS with impressive add-ons
   - Update PENALTY_SKILLS with anti-signals
   - Keep lists short and focused (10-40 items per category)

2. CONCEPT GROUPS:
   - Keep 8 concept dimensions (matches ALIGNMENT_SUB_WEIGHTS)
   - Replace keywords in each group with terms from new JD
   - Rename groups if dimensions don't apply (e.g., for frontend role)
   - Add sub-lists like PRODUCT_COMPANIES if needed

3. ALIASES:
   - Add common abbreviations (CEO, API, etc.)
   - Add common misspellings or variations
   - Add term equivalences (LLM ↔ Large Language Models)

4. VALIDATION:
   - Run validate_keywords() after changes
   - Check for duplicates (will fail validation)
   - Check for self-referential aliases

Example for different role (Senior Data Engineer):

REQUIRED_SKILLS = [
    "python", "sql", "data engineering", "apache spark", "etl",
    "data pipelines", "data modeling"
]

CONCEPT_GROUPS = [
    "sql_mastery", "spark_ecosystem", "etl_pipeline_design", "data_quality",
    "infrastructure", "cloud_platforms", "monitoring", "documentation"
]

And so on...
"""
