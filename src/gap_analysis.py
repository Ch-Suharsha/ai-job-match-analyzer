"""
gap_analysis.py
Fully defensive — handles string booleans, NaN, and empty dataframes.
"""

import json
from collections import Counter

import pandas as pd


def _to_bool(val) -> bool:
    """Convert any CSV boolean value to a real Python bool."""
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return bool(val)
    return str(val).strip().lower() in ("true", "1", "yes")


def top_missing_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    all_missing = []
    for row in df.get("missing_skills", []):
        if isinstance(row, list):
            all_missing.extend(row)
        elif isinstance(row, str) and row not in ("", "[]"):
            try:
                all_missing.extend(json.loads(row.replace("'", '"')))
            except Exception:
                pass
    counts = Counter(all_missing)
    return pd.DataFrame(counts.most_common(top_n), columns=["skill", "job_count"])


def top_matched_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    all_matched = []
    for row in df.get("matched_skills", []):
        if isinstance(row, list):
            all_matched.extend(row)
        elif isinstance(row, str) and row not in ("", "[]"):
            try:
                all_matched.extend(json.loads(row.replace("'", '"')))
            except Exception:
                pass
    counts = Counter(all_matched)
    return pd.DataFrame(counts.most_common(top_n), columns=["skill", "job_count"])


def tier_distribution(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Strong Match", "Good Match", "Partial Match", "Low Match"]
    dist = df["match_tier"].value_counts().reindex(order, fill_value=0).reset_index()
    dist.columns = ["tier", "count"]
    return dist


def agent_performance_metrics(df: pd.DataFrame) -> dict:
    """KPIs — fully defensive against string booleans and NaN values."""
    if df.empty:
        return {
            "total_jobs_analyzed": 0, "avg_match_score": 0.0,
            "median_match_score": 0.0, "strong_match_count": 0,
            "good_match_count": 0, "remote_job_pct": 0.0,
            "top_company": "N/A", "score_std": 0.0, "high_quality_rate": 0.0,
        }

    scores = pd.to_numeric(df["match_score"], errors="coerce").fillna(0)
    remote_bool = df["remote"].apply(_to_bool)

    return {
        "total_jobs_analyzed": len(df),
        "avg_match_score": round(float(scores.mean()), 1),
        "median_match_score": round(float(scores.median()), 1),
        "strong_match_count": int((df["match_tier"] == "Strong Match").sum()),
        "good_match_count": int((df["match_tier"] == "Good Match").sum()),
        "remote_job_pct": round(float(remote_bool.mean()) * 100, 1),
        "top_company": df["company"].value_counts().idxmax() if not df.empty else "N/A",
        "score_std": round(float(scores.std()), 1),
        "high_quality_rate": round(
            float(df["match_tier"].isin(["Strong Match", "Good Match"]).mean()) * 100, 1
        ),
    }
