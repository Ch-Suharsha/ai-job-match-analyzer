"""
matcher.py
Core ML matching engine.
Embeds candidate profile + job descriptions using sentence-transformers
then computes cosine similarity scores.
"""

import json
import os
import re

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "all-MiniLM-L6-v2"  # lightweight, CPU-friendly, 384-dim embeddings

SKILL_KEYWORDS = [
    "python", "sql", "r", "java", "scala", "spark", "kafka",
    "machine learning", "deep learning", "nlp", "llm",
    "tensorflow", "pytorch", "scikit-learn", "xgboost",
    "pandas", "numpy", "matplotlib", "plotly", "tableau", "power bi",
    "statistics", "a/b testing", "hypothesis testing",
    "airflow", "dbt", "etl", "data pipeline",
    "postgresql", "mysql", "mongodb", "snowflake", "bigquery", "redshift",
    "aws", "gcp", "azure", "docker", "kubernetes",
    "streamlit", "fastapi", "flask",
    "git", "github", "jupyter",
    "data visualization", "dashboarding", "reporting",
    "communication", "stakeholder", "cross-functional",
    "ai agent", "generative ai", "langchain", "openai",
]


def load_profile(path: str = "candidate_profile.json") -> dict:
    with open(path) as f:
        return json.load(f)


def load_jobs(path: str = "data/raw_jobs.json") -> list:
    with open(path) as f:
        return json.load(f)


def build_profile_text(profile: dict) -> str:
    """Combine profile fields into a single text blob for embedding."""
    skills_str = ", ".join(profile.get("skills", []))
    roles_str = ", ".join(profile.get("preferred_roles", []))
    return (
        f"{profile.get('summary', '')} "
        f"Skills: {skills_str}. "
        f"Target roles: {roles_str}. "
        f"Education: {profile.get('education', '')}."
    )


def clean_text(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def extract_skills(description: str) -> set:
    """Return skill keywords found in the job description."""
    desc_lower = description.lower()
    return {kw for kw in SKILL_KEYWORDS if kw in desc_lower}


def _tier(score: float) -> str:
    if score >= 0.75:
        return "Strong Match"
    if score >= 0.60:
        return "Good Match"
    if score >= 0.45:
        return "Partial Match"
    return "Low Match"


def run_matching(
    profile_path: str = "candidate_profile.json",
    jobs_path: str = "data/raw_jobs.json",
) -> pd.DataFrame:
    """
    Main pipeline: embed profile + jobs, compute cosine similarity,
    run gap analysis, return scored DataFrame.
    """
    print("Loading profile and jobs...")
    profile = load_profile(profile_path)
    jobs = load_jobs(jobs_path)

    print(f"Loaded {len(jobs)} jobs. Loading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    profile_text = build_profile_text(profile)
    profile_skills = {s.lower() for s in profile.get("skills", [])}
    profile_embedding = model.encode([profile_text])

    rows = []
    print("Scoring jobs...")
    for job in jobs:
        desc = clean_text(job.get("descriptionText", ""))
        if not desc:
            continue

        job_embedding = model.encode([desc])
        score = float(cosine_similarity(profile_embedding, job_embedding)[0][0])

        job_skills = extract_skills(desc)
        matched = profile_skills & job_skills
        missing = job_skills - profile_skills

        rows.append({
            "job_id": job.get("id", ""),
            "title": job.get("title", "Unknown"),
            "company": job.get("companyName", "Unknown"),
            "location": job.get("location", "Unknown"),
            "remote": job.get("workRemoteAllowed", False),
            "seniority": job.get("seniorityLevel", "Unknown"),
            "posted_at": job.get("postedAt", ""),
            "apply_url": job.get("applyUrl") or job.get("link", ""),
            "linkedin_url": job.get("link", ""),
            "match_score": round(score * 100, 1),
            "match_tier": _tier(score),
            "job_skills_found": sorted(job_skills),
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "match_pct_skills": round(
                len(matched) / len(job_skills) * 100, 1
            ) if job_skills else 0.0,
            "description_snippet": desc[:300],
        })

    df = (
        pd.DataFrame(rows)
        .sort_values("match_score", ascending=False)
        .reset_index(drop=True)
    )
    top = df.iloc[0]
    print(f"Top match: {top['match_score']}% — {top['title']} @ {top['company']}")
    return df


def save_results(df: pd.DataFrame, path: str = "data/match_results.csv") -> None:
    os.makedirs("data", exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Results saved to {path}")


if __name__ == "__main__":
    df = run_matching()
    save_results(df)
    print(df[["title", "company", "match_score", "match_tier"]].head(10).to_string())
