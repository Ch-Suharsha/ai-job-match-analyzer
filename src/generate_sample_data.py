"""
generate_sample_data.py
Generates realistic sample match results so the dashboard works
out of the box without needing an Apify API key.

Run:  python src/generate_sample_data.py
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)

COMPANIES = [
    "Jobright.ai", "OpenAI", "Anthropic", "Scale AI", "Cohere",
    "Hugging Face", "DataRobot", "Databricks", "Weights & Biases",
    "Replit", "Mistral AI", "Together AI", "Stability AI",
    "Runway ML", "Clarifai", "Snorkel AI", "LangChain",
]

TITLES = [
    "Data Analyst, New Grad", "ML Engineer - Entry Level",
    "AI Analyst", "Junior Data Scientist",
    "Machine Learning Analyst", "NLP Engineer, New Grad",
    "Data Analyst - AI Products", "Research Analyst",
    "Product Analyst", "MLOps Engineer",
]

LOCATIONS = [
    "United States", "San Francisco, CA", "New York, NY",
    "Austin, TX", "Seattle, WA", "Remote", "Boston, MA",
]

SKILL_POOL = [
    "python", "sql", "machine learning", "statistics", "pandas",
    "scikit-learn", "nlp", "data visualization", "tableau", "a/b testing",
    "pytorch", "tensorflow", "airflow", "docker", "aws",
    "communication", "stakeholder", "reporting", "ai agent",
    "fastapi", "streamlit", "xgboost", "postgresql", "git",
]

CANDIDATE_SKILLS = {
    "python", "sql", "pandas", "scikit-learn", "nlp",
    "statistics", "data visualization", "a/b testing",
    "streamlit", "fastapi", "machine learning", "git",
    "reporting", "communication", "xgboost", "postgresql",
}


def _tier(score: float) -> str:
    if score >= 75:
        return "Strong Match"
    if score >= 60:
        return "Good Match"
    if score >= 45:
        return "Partial Match"
    return "Low Match"


def generate_jobs(n: int = 35) -> list:
    jobs = []
    for i in range(n):
        job_skills = set(random.sample(SKILL_POOL, random.randint(5, 12)))
        matched = CANDIDATE_SKILLS & job_skills
        missing = job_skills - CANDIDATE_SKILLS
        base_score = len(matched) / max(len(job_skills), 1) * 100
        score = round(min(max(base_score + random.uniform(-8, 8), 20), 96), 1)
        days_ago = random.randint(0, 7)
        posted = (datetime.now() - timedelta(days=days_ago)).isoformat()

        jobs.append({
            "job_id": f"job_{i+1:04d}",
            "title": random.choice(TITLES),
            "company": random.choice(COMPANIES),
            "location": random.choice(LOCATIONS),
            "remote": random.choice([True, True, False]),
            "seniority": "Entry level",
            "posted_at": posted,
            "apply_url": f"https://jobright.ai/jobs/info/sample_{i+1}",
            "linkedin_url": f"https://www.linkedin.com/jobs/view/sample-{i+1}",
            "match_score": score,
            "match_tier": _tier(score),
            "job_skills_found": sorted(job_skills),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "match_pct_skills": round(
                len(matched) / max(len(job_skills), 1) * 100, 1
            ),
            "description_snippet": (
                f"Looking for a {random.choice(TITLES).lower()} "
                f"with skills in {', '.join(list(job_skills)[:5])}."
            ),
        })

    return sorted(jobs, key=lambda x: x["match_score"], reverse=True)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    jobs = generate_jobs(35)
    df = pd.DataFrame(jobs)
    df.to_csv("data/sample_results.csv", index=False)
    print(f"Generated {len(jobs)} sample jobs -> data/sample_results.csv")
    print(df[["title", "company", "match_score", "match_tier"]].head(10).to_string())
