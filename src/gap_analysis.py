"""
gap_analysis.py
Aggregates skill gap stats and agent performance KPIs
used by the Streamlit dashboard.
"""

import json
from collections import Counter

import pandas as pd


def top_missing_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Which skills appear most in JDs but are missing from the candidate profile?
    Tells the agent: what skills should the candidate prioritize acquiring?
    """
    all_missing = []
    for row in df["missing_skills"]:
        if isinstance(row, list):
            all_missing.extend(row)
        elif isinstance(row, str):
            try:
                all_missing.extend(json.loads(row.replace("'", '"')))
            except Exception:
                pass
    counts = Counter(all_missing)
    return pd.DataFrame(counts.most_common(top_n), columns=["skill", "job_count"])


def top_matched_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Which candidate skills appear most across matched jobs?"""
    all_matched = []
    for row in df["matched_skills"]:
        if isinstance(row, list):
            all_matched.extend(row)
        elif isinstance(row, str):
            try:
                all_matched.extend(json.loads(row.replace("'", '"')))
            except Exception:
                pass
    counts = Counter(all_matched)
    return pd.DataFrame(counts.most_common(top_n), columns=["skill", "job_count"])


def tier_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """How many jobs fall into each match tier?"""
    order = ["Strong Match", "Good Match", "Partial Match", "Low Match"]
    dist = df["match_tier"].value_counts().reindex(order, fill_value=0).reset_index()
    dist.columns = ["tier", "count"]
    return dist


def agent_performance_metrics(df: pd.DataFrame) -> dict:
    """
    High-level KPIs a data analyst would report to the product team
    to evaluate how well the AI matching agent is performing.
    """
    return {
        "total_jobs_analyzed": len(df),
        "avg_match_score": round(df["match_score"].mean(), 1),
        "median_match_score": round(df["match_score"].median(), 1),
        "strong_match_count": int((df["match_tier"] == "Strong Match").sum()),
        "good_match_count": int((df["match_tier"] == "Good Match").sum()),
        "remote_job_pct": round(df["remote"].mean() * 100, 1),
        "top_company": df["company"].value_counts().idxmax() if not df.empty else "N/A",
        "score_std": round(df["match_score"].std(), 1),
        "high_quality_rate": round(
            (df["match_tier"].isin(["Strong Match", "Good Match"])).mean() * 100, 1
        ),
    }
