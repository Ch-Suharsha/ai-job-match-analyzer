"""
dashboard/app.py — Streamlit Dashboard
AI Job Match Quality Analyzer

Shows agent performance KPIs, match score distribution,
skill gap analysis, and a ranked job leaderboard.
"""

import ast
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# path setup
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from gap_analysis import (
    agent_performance_metrics,
    tier_distribution,
    top_matched_skills,
    top_missing_skills,
)

# page config
st.set_page_config(
    page_title="AI Job Match Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #313244;
    }
</style>
""", unsafe_allow_html=True)

# paths
DATA_PATH = Path(__file__).parent.parent / "data" / "match_results.csv"
SAMPLE_PATH = Path(__file__).parent.parent / "data" / "sample_results.csv"
PROFILE_PATH = Path(__file__).parent.parent / "candidate_profile.json"


@st.cache_data
def load_data() -> pd.DataFrame:
    path = DATA_PATH if DATA_PATH.exists() else SAMPLE_PATH
    df = pd.read_csv(path)
    for col in ["job_skills_found", "matched_skills", "missing_skills"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_list)
    return df


def _parse_list(val):
    if isinstance(val, list):
        return val
    try:
        return ast.literal_eval(str(val))
    except Exception:
        return []


@st.cache_data
def load_profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


# sidebar
with st.sidebar:
    st.title("🎯 Job Match Analyzer")
    st.caption("AI Agent Performance Dashboard")
    st.divider()

    profile = load_profile()
    st.subheader("Candidate Profile")
    st.write(f"**{profile['name']}** — {profile['title']}")
    st.caption(profile["summary"])
    st.divider()

    df_full = load_data()
    tier_filter = st.multiselect(
        "Filter by Match Tier",
        options=["Strong Match", "Good Match", "Partial Match", "Low Match"],
        default=["Strong Match", "Good Match", "Partial Match", "Low Match"],
    )
    remote_only = st.checkbox("Remote roles only", value=False)
    min_score = st.slider("Minimum match score", 0, 100, 0)
    st.divider()
    st.caption("Built with sentence-transformers + Streamlit")

# filter
df = df_full.copy()
if tier_filter:
    df = df[df["match_tier"].isin(tier_filter)]
if remote_only:
    df = df[df["remote"] == True]
df = df[df["match_score"] >= min_score]

# header
st.title("🎯 AI Job Match Quality Analyzer")
st.caption(
    "Scores live job postings against a candidate profile using NLP embeddings. "
    "Surfaces skill gaps and agent performance metrics for data-driven decisions."
)
st.divider()

# KPI row
metrics = agent_performance_metrics(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Jobs Analyzed", metrics["total_jobs_analyzed"])
c2.metric("Avg Match Score", f"{metrics['avg_match_score']}%")
c3.metric("Strong Matches", metrics["strong_match_count"])
c4.metric("High Quality Rate", f"{metrics['high_quality_rate']}%")
c5.metric("Remote Jobs", f"{metrics['remote_job_pct']}%")

st.divider()

# charts row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Match Score Distribution")
    fig = px.histogram(
        df, x="match_score", nbins=20,
        color_discrete_sequence=["#cba6f7"],
        labels={"match_score": "Match Score (%)", "count": "Jobs"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cdd6f4",
        bargap=0.1,
    )
    fig.add_vline(
        x=metrics["avg_match_score"], line_dash="dash",
        line_color="#89b4fa", annotation_text="Avg",
        annotation_font_color="#89b4fa",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Match Tier Breakdown")
    tier_df = tier_distribution(df)
    fig2 = px.bar(
        tier_df, x="tier", y="count",
        color="tier",
        color_discrete_sequence=["#a6e3a1", "#89b4fa", "#fab387", "#f38ba8"],
        labels={"tier": "Tier", "count": "Number of Jobs"},
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#cdd6f4",
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

# charts row 2 — skill gaps
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("🔴 Skill Gaps — What Jobs Want That You Don't Have")
    st.caption(
        "Skills appearing most in job descriptions that aren't in the candidate profile. "
        "High-priority upskilling targets for the agent to surface."
    )
    missing_df = top_missing_skills(df, top_n=12)
    if not missing_df.empty:
        fig3 = px.bar(
            missing_df.sort_values("job_count"),
            x="job_count", y="skill", orientation="h",
            color_discrete_sequence=["#f38ba8"],
            labels={"job_count": "Jobs Requiring This Skill", "skill": ""},
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No skill gap data available.")

with col4:
    st.subheader("🟢 Matched Skills — Your Strongest Assets")
    st.caption(
        "Skills from your profile that appear most frequently across matched jobs. "
        "These are your biggest competitive advantages."
    )
    matched_df = top_matched_skills(df, top_n=12)
    if not matched_df.empty:
        fig4 = px.bar(
            matched_df.sort_values("job_count"),
            x="job_count", y="skill", orientation="h",
            color_discrete_sequence=["#a6e3a1"],
            labels={"job_count": "Jobs Matching This Skill", "skill": ""},
        )
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#cdd6f4",
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No matched skills data available.")

# job leaderboard
st.divider()
st.subheader("🏆 Job Match Leaderboard")
st.caption("Top-ranked jobs by match score.")

display_df = df[[
    "title", "company", "location", "match_score", "match_tier",
    "remote", "seniority", "match_pct_skills", "apply_url"
]].copy()
display_df["remote"] = display_df["remote"].map({True: "✅ Remote", False: "On-site"})
display_df.columns = [
    "Job Title", "Company", "Location", "Match Score (%)",
    "Tier", "Remote", "Seniority", "Skill Match (%)", "Apply URL"
]

st.dataframe(
    display_df.head(25),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Match Score (%)": st.column_config.ProgressColumn(
            "Match Score", min_value=0, max_value=100, format="%.1f%%"
        ),
        "Skill Match (%)": st.column_config.ProgressColumn(
            "Skill Match", min_value=0, max_value=100, format="%.0f%%"
        ),
        "Apply URL": st.column_config.LinkColumn("Apply"),
    }
)

# agent performance summary
st.divider()
st.subheader("📊 Agent Performance Summary")
st.caption(
    "Metrics a data analyst would report to the product team "
    "to evaluate how well the AI job matching agent is performing."
)

ins1, ins2, ins3 = st.columns(3)
with ins1:
    st.metric("Median Match Score", f"{metrics['median_match_score']}%")
    st.caption("50th percentile — how good is a typical match?")
with ins2:
    st.metric("Score Std Dev", f"{metrics['score_std']}%")
    st.caption("Consistency of matching. Lower = more reliable.")
with ins3:
    st.metric("Top Hiring Company", metrics["top_company"])
    st.caption("Most frequent company in matched results")
