"""
Curated seed catalogs for PRISM's synthetic 2022-2026 dataset.

These lists define WHAT exists (skill names, categories, lifecycle
archetypes, occupation->skill associations, industry->skill associations).
The actual per-year numbers (demand scores, growth rates, lifecycle
stages, relationships, transitions) are computed programmatically from
these catalogs in seed_generator.py — nothing numeric is hand-typed here.

This is clearly synthetic/demo data (see README + UI labeling), built to
be internally consistent, not a claim about real-world statistics.
"""

# Lifecycle archetypes drive the shape of the demand curve a skill is
# assigned in seed_generator.py:
#   emerging      -> low then steep late acceleration (e.g. AI Agents)
#   growing       -> steady, strong upward slope (e.g. RAG)
#   established   -> high, stable, slight upward drift (e.g. Python)
#   transforming  -> established skill whose usage context is shifting (e.g. Data Engineering)
#   declining     -> steady downward slope (e.g. jQuery)
#   ghost         -> already low and fading further (e.g. Legacy Mainframe COBOL Maintenance)

SKILLS = [
    # --- AI / ML / GenAI cluster ---
    {"name": "Generative AI", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Large Language Models", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Retrieval-Augmented Generation", "category": "AI/ML", "archetype": "emerging"},
    {"name": "AI Agents", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Prompt Engineering", "category": "AI/ML", "archetype": "growing"},
    {"name": "Vector Databases", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Semantic Search", "category": "AI/ML", "archetype": "growing"},
    {"name": "Fine-Tuning", "category": "AI/ML", "archetype": "growing"},
    {"name": "Tool Calling / Function Calling", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Context Engineering", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Multimodal AI", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Machine Learning", "category": "AI/ML", "archetype": "established"},
    {"name": "Deep Learning", "category": "AI/ML", "archetype": "established"},
    {"name": "Natural Language Processing", "category": "AI/ML", "archetype": "established"},
    {"name": "Computer Vision", "category": "AI/ML", "archetype": "established"},
    {"name": "MLOps", "category": "AI/ML", "archetype": "growing"},
    {"name": "Model Evaluation & Guardrails", "category": "AI/ML", "archetype": "emerging"},
    {"name": "AI Safety & Alignment", "category": "AI/ML", "archetype": "emerging"},
    {"name": "Reinforcement Learning", "category": "AI/ML", "archetype": "established"},
    {"name": "Recommender Systems", "category": "AI/ML", "archetype": "established"},

    # --- Data ---
    {"name": "SQL", "category": "Data", "archetype": "established"},
    {"name": "Python", "category": "Data", "archetype": "established"},
    {"name": "R Programming", "category": "Data", "archetype": "declining"},
    {"name": "Data Analysis", "category": "Data", "archetype": "established"},
    {"name": "Data Engineering", "category": "Data", "archetype": "transforming"},
    {"name": "Data Visualization", "category": "Data", "archetype": "established"},
    {"name": "ETL Pipelines", "category": "Data", "archetype": "transforming"},
    {"name": "Data Warehousing", "category": "Data", "archetype": "established"},
    {"name": "Big Data (Hadoop/Spark)", "category": "Data", "archetype": "declining"},
    {"name": "Statistics", "category": "Data", "archetype": "established"},
    {"name": "A/B Testing", "category": "Data", "archetype": "established"},
    {"name": "Data Governance", "category": "Data", "archetype": "growing"},
    {"name": "Real-Time Streaming (Kafka)", "category": "Data", "archetype": "growing"},
    {"name": "dbt (Data Build Tool)", "category": "Data", "archetype": "growing"},

    # --- Cloud / Infra ---
    {"name": "Cloud Computing (AWS)", "category": "Cloud & Infra", "archetype": "established"},
    {"name": "Cloud Computing (Azure)", "category": "Cloud & Infra", "archetype": "established"},
    {"name": "Cloud Computing (GCP)", "category": "Cloud & Infra", "archetype": "growing"},
    {"name": "Kubernetes", "category": "Cloud & Infra", "archetype": "established"},
    {"name": "Docker", "category": "Cloud & Infra", "archetype": "established"},
    {"name": "Infrastructure as Code (Terraform)", "category": "Cloud & Infra", "archetype": "growing"},
    {"name": "Serverless Architecture", "category": "Cloud & Infra", "archetype": "growing"},
    {"name": "CI/CD", "category": "Cloud & Infra", "archetype": "established"},
    {"name": "Site Reliability Engineering", "category": "Cloud & Infra", "archetype": "growing"},
    {"name": "GPU/Accelerator Infrastructure", "category": "Cloud & Infra", "archetype": "emerging"},
    {"name": "Edge Computing", "category": "Cloud & Infra", "archetype": "growing"},
    {"name": "On-Premise Server Administration", "category": "Cloud & Infra", "archetype": "ghost"},

    # --- Security ---
    {"name": "Cybersecurity Fundamentals", "category": "Security", "archetype": "established"},
    {"name": "Cloud Security", "category": "Security", "archetype": "growing"},
    {"name": "AI/LLM Security", "category": "Security", "archetype": "emerging"},
    {"name": "Identity & Access Management", "category": "Security", "archetype": "established"},
    {"name": "Penetration Testing", "category": "Security", "archetype": "established"},
    {"name": "Security Compliance (SOC2/ISO)", "category": "Security", "archetype": "growing"},
    {"name": "Zero Trust Architecture", "category": "Security", "archetype": "growing"},
    {"name": "Incident Response", "category": "Security", "archetype": "established"},

    # --- Software Engineering ---
    {"name": "JavaScript", "category": "Software Engineering", "archetype": "established"},
    {"name": "TypeScript", "category": "Software Engineering", "archetype": "growing"},
    {"name": "React", "category": "Software Engineering", "archetype": "established"},
    {"name": "Node.js", "category": "Software Engineering", "archetype": "established"},
    {"name": "Java", "category": "Software Engineering", "archetype": "established"},
    {"name": "Go", "category": "Software Engineering", "archetype": "growing"},
    {"name": "Rust", "category": "Software Engineering", "archetype": "emerging"},
    {"name": "API Engineering", "category": "Software Engineering", "archetype": "established"},
    {"name": "Microservices Architecture", "category": "Software Engineering", "archetype": "established"},
    {"name": "System Design", "category": "Software Engineering", "archetype": "established"},
    {"name": "jQuery", "category": "Software Engineering", "archetype": "ghost"},
    {"name": "AngularJS (Legacy)", "category": "Software Engineering", "archetype": "ghost"},
    {"name": "Flash/ActionScript", "category": "Software Engineering", "archetype": "ghost"},
    {"name": "PHP", "category": "Software Engineering", "archetype": "declining"},
    {"name": "Ruby on Rails", "category": "Software Engineering", "archetype": "declining"},
    {"name": "Legacy Mainframe (COBOL) Maintenance", "category": "Software Engineering", "archetype": "ghost"},
    {"name": "Test Automation", "category": "Software Engineering", "archetype": "established"},
    {"name": "AI-Assisted Coding Tools", "category": "Software Engineering", "archetype": "emerging"},

    # --- Product / Design ---
    {"name": "Product Management", "category": "Product & Design", "archetype": "established"},
    {"name": "Product Strategy", "category": "Product & Design", "archetype": "established"},
    {"name": "UX Research", "category": "Product & Design", "archetype": "established"},
    {"name": "UI Design", "category": "Product & Design", "archetype": "established"},
    {"name": "Design Systems", "category": "Product & Design", "archetype": "growing"},
    {"name": "AI Product Design", "category": "Product & Design", "archetype": "emerging"},
    {"name": "Roadmapping", "category": "Product & Design", "archetype": "established"},
    {"name": "User Research Synthesis", "category": "Product & Design", "archetype": "established"},

    # --- Business / Analytics ---
    {"name": "Business Analysis", "category": "Business", "archetype": "established"},
    {"name": "Financial Modeling", "category": "Business", "archetype": "established"},
    {"name": "Digital Marketing", "category": "Business", "archetype": "established"},
    {"name": "SEO", "category": "Business", "archetype": "declining"},
    {"name": "Marketing Analytics", "category": "Business", "archetype": "growing"},
    {"name": "Supply Chain Analytics", "category": "Business", "archetype": "growing"},
    {"name": "CRM Platforms (Salesforce)", "category": "Business", "archetype": "established"},
    {"name": "Revenue Operations", "category": "Business", "archetype": "growing"},
    {"name": "Growth Hacking", "category": "Business", "archetype": "declining"},

    # --- Healthcare ---
    {"name": "Clinical Data Management", "category": "Healthcare", "archetype": "established"},
    {"name": "Healthcare Interoperability (FHIR)", "category": "Healthcare", "archetype": "growing"},
    {"name": "Clinical NLP", "category": "Healthcare", "archetype": "emerging"},
    {"name": "Medical Imaging AI", "category": "Healthcare", "archetype": "emerging"},
    {"name": "Regulatory Affairs (Healthcare)", "category": "Healthcare", "archetype": "established"},
    {"name": "Telehealth Platforms", "category": "Healthcare", "archetype": "growing"},
    {"name": "Bioinformatics", "category": "Healthcare", "archetype": "established"},

    # --- Manufacturing / Energy ---
    {"name": "Industrial IoT", "category": "Manufacturing & Energy", "archetype": "growing"},
    {"name": "Predictive Maintenance AI", "category": "Manufacturing & Energy", "archetype": "emerging"},
    {"name": "Robotics Process Automation", "category": "Manufacturing & Energy", "archetype": "growing"},
    {"name": "Renewable Energy Systems", "category": "Manufacturing & Energy", "archetype": "growing"},
    {"name": "Lean Manufacturing", "category": "Manufacturing & Energy", "archetype": "established"},
    {"name": "Digital Twin Modeling", "category": "Manufacturing & Energy", "archetype": "emerging"},

    # --- Finance ---
    {"name": "Algorithmic Trading", "category": "Finance", "archetype": "established"},
    {"name": "Risk Modeling", "category": "Finance", "archetype": "established"},
    {"name": "Blockchain Development", "category": "Finance", "archetype": "declining"},
    {"name": "RegTech Compliance Automation", "category": "Finance", "archetype": "growing"},
    {"name": "AI-Driven Fraud Detection", "category": "Finance", "archetype": "emerging"},
    {"name": "Payments Infrastructure", "category": "Finance", "archetype": "established"},

    # --- Soft / cross-cutting ---
    {"name": "Stakeholder Communication", "category": "Cross-Cutting", "archetype": "established"},
    {"name": "Cross-Functional Leadership", "category": "Cross-Cutting", "archetype": "established"},
    {"name": "Technical Writing", "category": "Cross-Cutting", "archetype": "established"},
    {"name": "Change Management", "category": "Cross-Cutting", "archetype": "established"},
    {"name": "Data Storytelling", "category": "Cross-Cutting", "archetype": "growing"},
    {"name": "AI Literacy / Responsible AI Use", "category": "Cross-Cutting", "archetype": "emerging"},
]

# Occupations with the core skills that define them (skill name, weight 0-1).
# Weight = how central the skill is to the role, used for graph edges and
# to compute occupation-to-occupation transition overlap.
OCCUPATIONS = [
    {"title": "AI Engineer", "skills": [
        ("Large Language Models", 1.0), ("Retrieval-Augmented Generation", 0.95),
        ("AI Agents", 0.9), ("Vector Databases", 0.85), ("Prompt Engineering", 0.8),
        ("Python", 0.9), ("API Engineering", 0.7), ("Cloud Computing (AWS)", 0.6),
        ("MLOps", 0.6), ("Fine-Tuning", 0.6),
    ]},
    {"title": "Machine Learning Engineer", "skills": [
        ("Machine Learning", 1.0), ("Deep Learning", 0.9), ("Python", 0.95),
        ("MLOps", 0.85), ("Statistics", 0.7), ("Cloud Computing (AWS)", 0.6),
        ("Model Evaluation & Guardrails", 0.5), ("Data Engineering", 0.5),
    ]},
    {"title": "Data Scientist", "skills": [
        ("Statistics", 1.0), ("Python", 0.9), ("SQL", 0.85), ("Machine Learning", 0.85),
        ("Data Visualization", 0.7), ("A/B Testing", 0.65), ("Data Storytelling", 0.6),
        ("R Programming", 0.3),
    ]},
    {"title": "Data Analyst", "skills": [
        ("SQL", 1.0), ("Data Analysis", 0.95), ("Data Visualization", 0.85),
        ("Statistics", 0.6), ("Business Analysis", 0.55), ("Python", 0.5),
        ("A/B Testing", 0.4),
    ]},
    {"title": "Data Engineer", "skills": [
        ("Data Engineering", 1.0), ("ETL Pipelines", 0.9), ("SQL", 0.85),
        ("Python", 0.7), ("Data Warehousing", 0.75), ("Cloud Computing (AWS)", 0.65),
        ("Real-Time Streaming (Kafka)", 0.55), ("dbt (Data Build Tool)", 0.5),
    ]},
    {"title": "Analytics Engineer", "skills": [
        ("dbt (Data Build Tool)", 1.0), ("SQL", 0.9), ("Data Warehousing", 0.8),
        ("Data Visualization", 0.65), ("Data Governance", 0.5), ("Python", 0.4),
    ]},
    {"title": "MLOps Engineer", "skills": [
        ("MLOps", 1.0), ("Kubernetes", 0.85), ("CI/CD", 0.8), ("Docker", 0.75),
        ("Cloud Computing (AWS)", 0.7), ("Python", 0.6), ("Model Evaluation & Guardrails", 0.55),
    ]},
    {"title": "Product Analyst", "skills": [
        ("Data Analysis", 1.0), ("SQL", 0.85), ("A/B Testing", 0.8),
        ("Product Strategy", 0.55), ("Data Visualization", 0.7), ("Data Storytelling", 0.6),
    ]},
    {"title": "AI Product Manager", "skills": [
        ("Product Strategy", 1.0), ("AI Product Design", 0.85), ("Roadmapping", 0.8),
        ("Stakeholder Communication", 0.75), ("Generative AI", 0.6), ("Data Analysis", 0.5),
        ("AI Literacy / Responsible AI Use", 0.5),
    ]},
    {"title": "Product Manager", "skills": [
        ("Product Strategy", 1.0), ("Roadmapping", 0.9), ("Stakeholder Communication", 0.8),
        ("UX Research", 0.5), ("Data Analysis", 0.55), ("Cross-Functional Leadership", 0.6),
    ]},
    {"title": "UX Designer", "skills": [
        ("UI Design", 1.0), ("UX Research", 0.9), ("Design Systems", 0.7),
        ("User Research Synthesis", 0.75), ("Stakeholder Communication", 0.5),
    ]},
    {"title": "AI Product Designer", "skills": [
        ("AI Product Design", 1.0), ("UI Design", 0.8), ("UX Research", 0.75),
        ("Design Systems", 0.6), ("Prompt Engineering", 0.4),
    ]},
    {"title": "Software Engineer", "skills": [
        ("JavaScript", 0.9), ("TypeScript", 0.7), ("React", 0.7), ("Node.js", 0.7),
        ("System Design", 0.6), ("API Engineering", 0.7), ("Test Automation", 0.5),
        ("AI-Assisted Coding Tools", 0.5),
    ]},
    {"title": "Backend Engineer", "skills": [
        ("API Engineering", 1.0), ("Microservices Architecture", 0.85), ("Java", 0.6),
        ("Go", 0.5), ("SQL", 0.6), ("System Design", 0.75), ("Docker", 0.6),
    ]},
    {"title": "Frontend Engineer", "skills": [
        ("JavaScript", 1.0), ("TypeScript", 0.85), ("React", 0.9),
        ("Design Systems", 0.5), ("UI Design", 0.4),
    ]},
    {"title": "Full-Stack Engineer", "skills": [
        ("JavaScript", 0.9), ("React", 0.8), ("Node.js", 0.8), ("SQL", 0.6),
        ("API Engineering", 0.7), ("Cloud Computing (AWS)", 0.5),
    ]},
    {"title": "Site Reliability Engineer", "skills": [
        ("Site Reliability Engineering", 1.0), ("Kubernetes", 0.9), ("CI/CD", 0.75),
        ("Cloud Computing (AWS)", 0.7), ("Incident Response", 0.6), ("Docker", 0.65),
    ]},
    {"title": "Cloud Architect", "skills": [
        ("Cloud Computing (AWS)", 1.0), ("Cloud Computing (Azure)", 0.6),
        ("Infrastructure as Code (Terraform)", 0.8), ("Kubernetes", 0.7),
        ("System Design", 0.7), ("Cloud Security", 0.55),
    ]},
    {"title": "DevOps Engineer", "skills": [
        ("CI/CD", 1.0), ("Docker", 0.85), ("Kubernetes", 0.8),
        ("Infrastructure as Code (Terraform)", 0.75), ("Cloud Computing (AWS)", 0.7),
    ]},
    {"title": "Security Engineer", "skills": [
        ("Cybersecurity Fundamentals", 1.0), ("Cloud Security", 0.8),
        ("Identity & Access Management", 0.7), ("Penetration Testing", 0.65),
        ("Incident Response", 0.6), ("Zero Trust Architecture", 0.55),
    ]},
    {"title": "AI Security Engineer", "skills": [
        ("AI/LLM Security", 1.0), ("Cybersecurity Fundamentals", 0.7),
        ("Model Evaluation & Guardrails", 0.65), ("Large Language Models", 0.55),
        ("Cloud Security", 0.5),
    ]},
    {"title": "Security Compliance Analyst", "skills": [
        ("Security Compliance (SOC2/ISO)", 1.0), ("Cybersecurity Fundamentals", 0.6),
        ("Identity & Access Management", 0.5), ("Regulatory Affairs (Healthcare)", 0.2),
    ]},
    {"title": "Marketing Analyst", "skills": [
        ("Marketing Analytics", 1.0), ("Digital Marketing", 0.8), ("SQL", 0.5),
        ("Data Visualization", 0.6), ("SEO", 0.4),
    ]},
    {"title": "Growth Marketer", "skills": [
        ("Growth Hacking", 1.0), ("Digital Marketing", 0.85), ("Marketing Analytics", 0.6),
        ("SEO", 0.5), ("A/B Testing", 0.55),
    ]},
    {"title": "Revenue Operations Analyst", "skills": [
        ("Revenue Operations", 1.0), ("CRM Platforms (Salesforce)", 0.8),
        ("Data Analysis", 0.6), ("Financial Modeling", 0.4),
    ]},
    {"title": "Business Analyst", "skills": [
        ("Business Analysis", 1.0), ("SQL", 0.6), ("Financial Modeling", 0.55),
        ("Stakeholder Communication", 0.65), ("Data Visualization", 0.5),
    ]},
    {"title": "Financial Analyst", "skills": [
        ("Financial Modeling", 1.0), ("Business Analysis", 0.6), ("Risk Modeling", 0.5),
        ("Data Analysis", 0.55),
    ]},
    {"title": "Supply Chain Analyst", "skills": [
        ("Supply Chain Analytics", 1.0), ("Data Analysis", 0.7), ("SQL", 0.5),
        ("Predictive Maintenance AI", 0.3),
    ]},
    {"title": "Clinical Data Analyst", "skills": [
        ("Clinical Data Management", 1.0), ("Healthcare Interoperability (FHIR)", 0.6),
        ("SQL", 0.6), ("Statistics", 0.55), ("Regulatory Affairs (Healthcare)", 0.5),
    ]},
    {"title": "Clinical NLP Engineer", "skills": [
        ("Clinical NLP", 1.0), ("Natural Language Processing", 0.8),
        ("Large Language Models", 0.6), ("Clinical Data Management", 0.5), ("Python", 0.6),
    ]},
    {"title": "Medical Imaging AI Engineer", "skills": [
        ("Medical Imaging AI", 1.0), ("Computer Vision", 0.85), ("Deep Learning", 0.7),
        ("Python", 0.6), ("Regulatory Affairs (Healthcare)", 0.4),
    ]},
    {"title": "Bioinformatics Scientist", "skills": [
        ("Bioinformatics", 1.0), ("Statistics", 0.7), ("Python", 0.6), ("Machine Learning", 0.5),
    ]},
    {"title": "Telehealth Product Manager", "skills": [
        ("Telehealth Platforms", 1.0), ("Product Strategy", 0.7),
        ("Healthcare Interoperability (FHIR)", 0.5), ("Stakeholder Communication", 0.5),
    ]},
    {"title": "Industrial IoT Engineer", "skills": [
        ("Industrial IoT", 1.0), ("Predictive Maintenance AI", 0.7),
        ("Edge Computing", 0.6), ("Python", 0.5), ("Digital Twin Modeling", 0.5),
    ]},
    {"title": "Robotics Automation Engineer", "skills": [
        ("Robotics Process Automation", 1.0), ("Industrial IoT", 0.5),
        ("Lean Manufacturing", 0.5), ("Python", 0.5),
    ]},
    {"title": "Renewable Energy Systems Engineer", "skills": [
        ("Renewable Energy Systems", 1.0), ("Digital Twin Modeling", 0.4),
        ("Industrial IoT", 0.4), ("Predictive Maintenance AI", 0.4),
    ]},
    {"title": "Quantitative Analyst", "skills": [
        ("Algorithmic Trading", 1.0), ("Risk Modeling", 0.85), ("Statistics", 0.8),
        ("Python", 0.75), ("Machine Learning", 0.5),
    ]},
    {"title": "Risk Analyst", "skills": [
        ("Risk Modeling", 1.0), ("Financial Modeling", 0.65), ("Statistics", 0.7),
        ("SQL", 0.5), ("AI-Driven Fraud Detection", 0.4),
    ]},
    {"title": "Blockchain Developer", "skills": [
        ("Blockchain Development", 1.0), ("API Engineering", 0.5), ("JavaScript", 0.4),
    ]},
    {"title": "Fraud Detection Analyst", "skills": [
        ("AI-Driven Fraud Detection", 1.0), ("Machine Learning", 0.6), ("SQL", 0.6),
        ("Risk Modeling", 0.5), ("Payments Infrastructure", 0.4),
    ]},
    {"title": "Compliance Automation Engineer", "skills": [
        ("RegTech Compliance Automation", 1.0), ("Security Compliance (SOC2/ISO)", 0.6),
        ("Python", 0.4), ("API Engineering", 0.4),
    ]},
    {"title": "Technical Writer", "skills": [
        ("Technical Writing", 1.0), ("Stakeholder Communication", 0.6),
        ("API Engineering", 0.3), ("AI Literacy / Responsible AI Use", 0.3),
    ]},
    {"title": "Engineering Manager", "skills": [
        ("Cross-Functional Leadership", 1.0), ("System Design", 0.6),
        ("Stakeholder Communication", 0.7), ("Change Management", 0.5), ("CI/CD", 0.3),
    ]},
    {"title": "Solutions Architect", "skills": [
        ("System Design", 1.0), ("Cloud Computing (AWS)", 0.75), ("Microservices Architecture", 0.65),
        ("Stakeholder Communication", 0.6), ("API Engineering", 0.6),
    ]},
    {"title": "AI Research Scientist", "skills": [
        ("Deep Learning", 1.0), ("Reinforcement Learning", 0.6), ("Large Language Models", 0.85),
        ("AI Safety & Alignment", 0.6), ("Python", 0.8), ("Multimodal AI", 0.6),
    ]},
    {"title": "Applied Scientist (Recommenders)", "skills": [
        ("Recommender Systems", 1.0), ("Machine Learning", 0.8), ("Python", 0.7),
        ("A/B Testing", 0.6), ("Statistics", 0.6),
    ]},
    {"title": "Computer Vision Engineer", "skills": [
        ("Computer Vision", 1.0), ("Deep Learning", 0.8), ("Python", 0.7),
        ("Medical Imaging AI", 0.3), ("MLOps", 0.4),
    ]},
    {"title": "NLP Engineer", "skills": [
        ("Natural Language Processing", 1.0), ("Large Language Models", 0.8),
        ("Python", 0.75), ("Fine-Tuning", 0.55), ("Clinical NLP", 0.2),
    ]},
    {"title": "Data Governance Analyst", "skills": [
        ("Data Governance", 1.0), ("SQL", 0.5), ("Security Compliance (SOC2/ISO)", 0.4),
        ("Data Warehousing", 0.4),
    ]},
    {"title": "Digital Twin Engineer", "skills": [
        ("Digital Twin Modeling", 1.0), ("Industrial IoT", 0.6), ("Python", 0.5),
        ("Predictive Maintenance AI", 0.5),
    ]},
    {"title": "Legacy Systems Maintainer", "skills": [
        ("Legacy Mainframe (COBOL) Maintenance", 1.0), ("On-Premise Server Administration", 0.6),
        ("System Design", 0.3),
    ]},
    {"title": "PHP Web Developer", "skills": [
        ("PHP", 1.0), ("JavaScript", 0.5), ("SQL", 0.5), ("jQuery", 0.4),
    ]},
    {"title": "Rails Developer", "skills": [
        ("Ruby on Rails", 1.0), ("SQL", 0.5), ("JavaScript", 0.4),
    ]},
    {"title": "SEO Specialist", "skills": [
        ("SEO", 1.0), ("Digital Marketing", 0.6), ("Marketing Analytics", 0.4),
    ]},
    {"title": "Systems Administrator", "skills": [
        ("On-Premise Server Administration", 1.0), ("Cybersecurity Fundamentals", 0.4),
        ("Cloud Computing (AWS)", 0.3),
    ]},
]

# Industries with their characteristic skill categories/skills (used to
# build industry_skills; weight = relative concentration).
INDUSTRIES = [
    {"name": "Software", "core_categories": ["Software Engineering", "Cloud & Infra", "AI/ML"]},
    {"name": "FinTech", "core_categories": ["Finance", "Data", "AI/ML", "Security"]},
    {"name": "Healthcare", "core_categories": ["Healthcare", "AI/ML", "Data"]},
    {"name": "Retail & E-commerce", "core_categories": ["Business", "Data", "AI/ML"]},
    {"name": "Manufacturing", "core_categories": ["Manufacturing & Energy", "Cloud & Infra"]},
    {"name": "Energy", "core_categories": ["Manufacturing & Energy", "Data"]},
    {"name": "Telecommunications", "core_categories": ["Cloud & Infra", "Software Engineering"]},
    {"name": "Insurance", "core_categories": ["Finance", "Data", "Security"]},
    {"name": "Banking", "core_categories": ["Finance", "Security", "Data"]},
    {"name": "Media & Entertainment", "core_categories": ["Product & Design", "AI/ML", "Software Engineering"]},
    {"name": "Education Technology", "core_categories": ["AI/ML", "Product & Design", "Data"]},
    {"name": "Government", "core_categories": ["Security", "Data", "Cloud & Infra"]},
    {"name": "Logistics & Supply Chain", "core_categories": ["Business", "Manufacturing & Energy", "Data"]},
    {"name": "Automotive", "core_categories": ["Manufacturing & Energy", "AI/ML", "Cloud & Infra"]},
    {"name": "Aerospace & Defense", "core_categories": ["Security", "Manufacturing & Energy", "Software Engineering"]},
    {"name": "Pharmaceuticals", "core_categories": ["Healthcare", "Data"]},
    {"name": "Consulting", "core_categories": ["Business", "Cross-Cutting", "AI/ML"]},
    {"name": "Real Estate", "core_categories": ["Business", "Data"]},
    {"name": "Travel & Hospitality", "core_categories": ["Business", "AI/ML", "Product & Design"]},
    {"name": "Legal Services", "core_categories": ["Cross-Cutting", "AI/ML", "Security"]},
    {"name": "Agriculture Technology", "core_categories": ["Manufacturing & Energy", "AI/ML", "Data"]},
    {"name": "Non-Profit & Public Sector", "core_categories": ["Cross-Cutting", "Data"]},
]

LOCATIONS = [
    {"city": "San Francisco", "region": "California", "country": "United States", "lat": 37.7749, "lon": -122.4194},
    {"city": "New York", "region": "New York", "country": "United States", "lat": 40.7128, "lon": -74.0060},
    {"city": "Austin", "region": "Texas", "country": "United States", "lat": 30.2672, "lon": -97.7431},
    {"city": "Seattle", "region": "Washington", "country": "United States", "lat": 47.6062, "lon": -122.3321},
    {"city": "Toronto", "region": "Ontario", "country": "Canada", "lat": 43.6532, "lon": -79.3832},
    {"city": "London", "region": "England", "country": "United Kingdom", "lat": 51.5072, "lon": -0.1276},
    {"city": "Berlin", "region": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050},
    {"city": "Amsterdam", "region": "North Holland", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
    {"city": "Paris", "region": "Île-de-France", "country": "France", "lat": 48.8566, "lon": 2.3522},
    {"city": "Bengaluru", "region": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
    {"city": "Hyderabad", "region": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867},
    {"city": "Pune", "region": "Maharashtra", "country": "India", "lat": 18.5204, "lon": 73.8567},
    {"city": "Singapore", "region": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"city": "Sydney", "region": "New South Wales", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
    {"city": "São Paulo", "region": "São Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333},
]

EDUCATION_PROGRAMS = [
    {"name": "B.Sc. Computer Science (Generic University Curriculum)", "type": "University Program",
     "skills": ["Python", "SQL", "Statistics", "Data Analysis", "System Design", "Java"]},
    {"name": "M.Sc. Data Science (Generic University Curriculum)", "type": "University Program",
     "skills": ["Python", "Statistics", "Machine Learning", "SQL", "Data Visualization"]},
    {"name": "Generic Coding Bootcamp — Full-Stack Web", "type": "Bootcamp",
     "skills": ["JavaScript", "React", "Node.js", "SQL", "API Engineering"]},
    {"name": "Generic Coding Bootcamp — Data Analytics", "type": "Bootcamp",
     "skills": ["SQL", "Python", "Data Visualization", "Statistics"]},
    {"name": "Cloud Practitioner Certification (Generic)", "type": "Certification",
     "skills": ["Cloud Computing (AWS)", "CI/CD", "Docker"]},
    {"name": "Machine Learning Specialization (Generic MOOC)", "type": "Online Course",
     "skills": ["Machine Learning", "Python", "Statistics", "Deep Learning"]},
    {"name": "Cybersecurity Fundamentals Certificate (Generic)", "type": "Certification",
     "skills": ["Cybersecurity Fundamentals", "Identity & Access Management", "Incident Response"]},
    {"name": "MBA — Generic Program", "type": "University Program",
     "skills": ["Business Analysis", "Financial Modeling", "Stakeholder Communication", "Cross-Functional Leadership"]},
    {"name": "UX Design Bootcamp (Generic)", "type": "Bootcamp",
     "skills": ["UI Design", "UX Research", "Design Systems"]},
    {"name": "Product Management Certificate (Generic)", "type": "Certification",
     "skills": ["Product Strategy", "Roadmapping", "Stakeholder Communication"]},
]
