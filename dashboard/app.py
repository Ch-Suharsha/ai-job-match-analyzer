"""
dashboard/app.py — AI Job Match Quality Analyzer
Luxury editorial design. Gold on obsidian. Playfair Display.
"""

import ast
import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from gap_analysis import (
    agent_performance_metrics,
    tier_distribution,
    top_matched_skills,
    top_missing_skills,
)

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orbis · Job Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── luxury CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,700;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=DM+Mono:wght@300;400&display=swap');

/* ── reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background: #080603 !important;
    color: #E8D9B8 !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
}

[data-testid="stSidebar"] { background: #0E0B07 !important; border-right: 1px solid #2A2218 !important; }
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stHeader"] { background: transparent !important; }

.block-container { padding: 0 3rem 4rem 3rem !important; max-width: 1400px !important; }

/* scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080603; }
::-webkit-scrollbar-thumb { background: #C9A84C44; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #C9A84C88; }

/* ── masthead ── */
.orbis-masthead {
    border-bottom: 1px solid #2A2218;
    padding: 3.5rem 0 2.5rem 0;
    margin-bottom: 3rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    animation: fadeUp 0.9s ease both;
}
.orbis-wordmark {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 400;
    letter-spacing: 0.18em;
    color: #E8D9B8;
    line-height: 1;
}
.orbis-wordmark span { color: #C9A84C; font-style: italic; }
.orbis-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.25em;
    color: #6B5A3E;
    text-transform: uppercase;
    text-align: right;
    line-height: 1.8;
}
.orbis-edition {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #C9A84C88;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── section labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.3em;
    color: #C9A84C;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    animation: fadeUp 0.9s ease both;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #2A2218, transparent);
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: #1E1810;
    border: 1px solid #1E1810;
    margin-bottom: 3.5rem;
    animation: fadeUp 0.9s 0.1s ease both;
}
.kpi-card {
    background: #0E0B07;
    padding: 2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: background 0.3s ease;
}
.kpi-card:hover { background: #131009; }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(to right, transparent, #C9A84C44, transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.kpi-card:hover::before { opacity: 1; }
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.25em;
    color: #6B5A3E;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: #E8D9B8;
    line-height: 1;
    letter-spacing: -0.01em;
}
.kpi-value.gold { color: #C9A84C; }
.kpi-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: #3D3020;
    margin-top: 0.6rem;
    letter-spacing: 0.1em;
}

/* ── chart panels ── */
.chart-panel {
    background: #0A0804;
    border: 1px solid #1E1810;
    padding: 2rem;
    margin-bottom: 1px;
    animation: fadeUp 0.9s 0.2s ease both;
}
.chart-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 400;
    font-style: italic;
    color: #D4C4A0;
    margin-bottom: 0.4rem;
}
.chart-caption {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: #4A3D28;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* ── leaderboard ── */
.leaderboard-row {
    display: grid;
    grid-template-columns: 2.5rem 1fr 1fr 8rem 6rem 5rem;
    gap: 0;
    border-bottom: 1px solid #1A1510;
    padding: 1.1rem 0;
    transition: background 0.2s ease;
    animation: fadeUp 0.6s ease both;
}
.leaderboard-row:hover { background: #0E0B0744; }
.leaderboard-header {
    grid-template-columns: 2.5rem 1fr 1fr 8rem 6rem 5rem;
    border-bottom: 1px solid #2A2218 !important;
    padding-bottom: 0.8rem !important;
}
.lb-rank {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.8rem;
    color: #3D3020;
    font-style: italic;
    padding-top: 0.1rem;
}
.lb-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: #D4C4A0;
    font-weight: 500;
}
.lb-company {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #6B5A3E;
    letter-spacing: 0.08em;
    margin-top: 0.25rem;
}
.lb-location {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #4A3D28;
    letter-spacing: 0.05em;
    padding-top: 0.15rem;
}
.lb-score-wrap { display: flex; flex-direction: column; gap: 0.3rem; }
.lb-score-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #C9A84C;
    font-weight: 400;
}
.lb-score-bar-bg {
    height: 2px;
    background: #1E1810;
    border-radius: 1px;
    overflow: hidden;
    width: 100%;
}
.lb-score-bar {
    height: 2px;
    background: linear-gradient(to right, #8B5E3C, #C9A84C);
    border-radius: 1px;
}
.lb-tier {
    font-family: 'DM Mono', monospace;
    font-size: 0.52rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.25rem 0.6rem;
    border-radius: 1px;
    display: inline-block;
    align-self: flex-start;
    margin-top: 0.1rem;
}
.tier-strong { background: #1A2A1A; color: #7CAE7A; border: 1px solid #2A402A; }
.tier-good   { background: #1A1F2A; color: #7A9CBE; border: 1px solid #2A3040; }
.tier-partial { background: #2A1F14; color: #BE9A6A; border: 1px solid #402E1A; }
.tier-low    { background: #2A1414; color: #BE7A7A; border: 1px solid #402020; }
.lb-remote {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: #4A3D28;
    letter-spacing: 0.05em;
    padding-top: 0.2rem;
}
.lb-apply {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #C9A84C;
    text-decoration: none;
    border: 1px solid #2A2218;
    padding: 0.3rem 0.8rem;
    display: inline-block;
    transition: all 0.2s ease;
    margin-top: 0.05rem;
}
.lb-apply:hover {
    background: #C9A84C11;
    border-color: #C9A84C44;
    color: #E8D9B8;
}

/* ── agent summary cards ── */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: #1E1810;
    border: 1px solid #1E1810;
    margin-top: 1rem;
    animation: fadeUp 0.9s 0.3s ease both;
}
.summary-card {
    background: #0A0804;
    padding: 2rem;
}
.summary-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #C9A84C;
    font-weight: 400;
    margin-bottom: 0.5rem;
}
.summary-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    color: #6B5A3E;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.summary-caption {
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.85rem;
    color: #3D3020;
    font-style: italic;
    line-height: 1.5;
}

/* ── sidebar ── */
.sidebar-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #E8D9B8;
    letter-spacing: 0.15em;
    margin-bottom: 0.3rem;
}
.sidebar-logo span { color: #C9A84C; font-style: italic; }
.sidebar-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.25em;
    color: #4A3D28;
    text-transform: uppercase;
    margin: 1.5rem 0 0.6rem 0;
}
.sidebar-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: #A89470;
    line-height: 1.6;
}

/* ── streamlit overrides ── */
[data-testid="stSlider"] label,
[data-testid="stCheckbox"] label,
[data-testid="stMultiSelect"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.2em !important;
    color: #4A3D28 !important;
    text-transform: uppercase !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: #C9A84C !important;
    border-color: #C9A84C !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #1E1810 !important;
    border: 1px solid #2A2218 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="base-input"] > input {
    background: #0E0B07 !important;
    border-color: #2A2218 !important;
    color: #A89470 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
}
[data-testid="stCheckbox"] input:checked + div {
    background: #C9A84C !important;
    border-color: #C9A84C !important;
}

/* hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="collapsedControl"] { color: #4A3D28 !important; }

/* ── animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* stagger animation delays for rows */
.delay-1 { animation-delay: 0.05s; }
.delay-2 { animation-delay: 0.10s; }
.delay-3 { animation-delay: 0.15s; }
.delay-4 { animation-delay: 0.20s; }
.delay-5 { animation-delay: 0.25s; }

/* divider */
.lux-divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #2A2218 30%, #2A2218 70%, transparent);
    margin: 3rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── paths & helpers ────────────────────────────────────────────────────────────
DATA_PATH   = Path(__file__).parent.parent / "data" / "match_results.csv"
SAMPLE_PATH = Path(__file__).parent.parent / "data" / "sample_results.csv"
PROFILE_PATH = Path(__file__).parent.parent / "candidate_profile.json"

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#6B5A3E", size=10),
    margin=dict(l=8, r=8, t=8, b=8),
    showlegend=False,
)
GRID_STYLE = dict(gridcolor="#1A1510", gridwidth=1)
AXIS_STYLE = dict(
    showgrid=True, gridcolor="#1A1510", gridwidth=1,
    zeroline=False, showline=False,
    tickfont=dict(family="DM Mono, monospace", size=9, color="#4A3D28"),
    title_font=dict(family="DM Mono, monospace", size=9, color="#4A3D28"),
)
GOLD  = "#C9A84C"
AMBER = "#8B5E3C"
IVORY = "#D4C4A0"
GREEN = "#5A8A58"
BLUE  = "#5A7A9A"
RUST  = "#9A5A3A"
RED   = "#8A3A3A"


def _parse_list(val):
    if isinstance(val, list): return val
    try: return ast.literal_eval(str(val))
    except: return []


@st.cache_data
def load_data() -> pd.DataFrame:
    path = DATA_PATH if DATA_PATH.exists() else SAMPLE_PATH
    df = pd.read_csv(path)
    for col in ["job_skills_found", "matched_skills", "missing_skills"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_list)
    return df


@st.cache_data
def load_profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def tier_class(tier: str) -> str:
    return {
        "Strong Match": "tier-strong",
        "Good Match":   "tier-good",
        "Partial Match":"tier-partial",
        "Low Match":    "tier-low",
    }.get(tier, "tier-low")


# ── sidebar ────────────────────────────────────────────────────────────────────
profile = load_profile()
df_full = load_data()

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 1.5rem 0 1rem 0; border-bottom: 1px solid #1E1810; margin-bottom: 1rem;">
        <div class="sidebar-logo">OR<span>B</span>IS</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.52rem;letter-spacing:0.22em;
                    color:#3D3020;text-transform:uppercase;margin-top:0.3rem;">
            Intelligence Platform
        </div>
    </div>
    <div class="sidebar-label">Candidate</div>
    <div class="sidebar-value">{profile['name']}</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#4A3D28;
                letter-spacing:0.05em;margin-top:0.2rem;">{profile['title']}</div>
    <div class="sidebar-label" style="margin-top:1.2rem;">Profile</div>
    <div style="font-family:'Cormorant Garamond',serif;font-size:0.85rem;color:#3D3020;
                font-style:italic;line-height:1.6;">{profile['summary'][:120]}…</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label" style="margin-top:1.5rem;">Filters</div>', unsafe_allow_html=True)

    tier_filter = st.multiselect(
        "Match Tier",
        options=["Strong Match", "Good Match", "Partial Match", "Low Match"],
        default=["Strong Match", "Good Match", "Partial Match", "Low Match"],
        label_visibility="collapsed",
    )
    remote_only = st.checkbox("Remote only", value=False)
    min_score   = st.slider("Min score", 0, 100, 0, label_visibility="collapsed")

    st.markdown("""
    <div style="border-top:1px solid #1E1810;margin-top:2rem;padding-top:1rem;">
        <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                    color:#2A2018;text-transform:uppercase;">
            Built with sentence-transformers<br>& Streamlit
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── filter ─────────────────────────────────────────────────────────────────────
df = df_full.copy()
if tier_filter:
    df = df[df["match_tier"].isin(tier_filter)]
if remote_only:
    df = df[df["remote"] == True]
df = df[df["match_score"] >= min_score]

metrics = agent_performance_metrics(df)

# ── masthead ───────────────────────────────────────────────────────────────────
from datetime import datetime
today = datetime.now().strftime("%d %B %Y").upper()

st.markdown(f"""
<div class="orbis-masthead">
    <div>
        <div class="orbis-wordmark">OR<span>B</span>IS</div>
        <div class="orbis-edition">Job Intelligence Platform · Private Edition</div>
    </div>
    <div class="orbis-tagline">
        {today}<br>
        {metrics['total_jobs_analyzed']} Positions Analysed<br>
        AI Matching Intelligence
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Performance Overview</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Positions Analysed</div>
        <div class="kpi-value">{metrics['total_jobs_analyzed']}</div>
        <div class="kpi-sub">Current dataset</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Average Match</div>
        <div class="kpi-value gold">{metrics['avg_match_score']}<span style="font-size:1.2rem;color:#6B5A3E">%</span></div>
        <div class="kpi-sub">Semantic similarity</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Strong Matches</div>
        <div class="kpi-value">{metrics['strong_match_count']}</div>
        <div class="kpi-sub">Score ≥ 75%</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Quality Rate</div>
        <div class="kpi-value gold">{metrics['high_quality_rate']}<span style="font-size:1.2rem;color:#6B5A3E">%</span></div>
        <div class="kpi-sub">Strong + Good tier</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Remote Eligible</div>
        <div class="kpi-value">{metrics['remote_job_pct']}<span style="font-size:1.2rem;color:#6B5A3E">%</span></div>
        <div class="kpi-sub">Of total matches</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── chart row 1 ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Distribution Intelligence</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2], gap="small")

with col1:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Match Score Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Semantic similarity across all analysed positions</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["match_score"], nbinsx=20,
        marker_color=GOLD, marker_line_color=AMBER,
        marker_line_width=0.5, opacity=0.85,
        hovertemplate="Score: %{x:.0f}%<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(
        x=metrics["avg_match_score"],
        line_dash="dot", line_color="#E8D9B844", line_width=1,
        annotation_text=f"avg {metrics['avg_match_score']}%",
        annotation_font=dict(family="DM Mono, monospace", size=9, color="#E8D9B866"),
        annotation_position="top right",
    )
    fig.update_layout(**CHART_LAYOUT, height=260,
        xaxis=dict(**AXIS_STYLE, title="Match Score (%)"),
        yaxis=dict(**AXIS_STYLE, title="Positions"),
        bargap=0.06,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Tier Composition</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Quality tier breakdown</div>', unsafe_allow_html=True)

    tier_df = tier_distribution(df)
    tier_colors = {"Strong Match": GREEN, "Good Match": BLUE, "Partial Match": RUST, "Low Match": RED}
    colors = [tier_colors.get(t, GOLD) for t in tier_df["tier"]]

    fig2 = go.Figure(go.Bar(
        x=tier_df["count"], y=tier_df["tier"],
        orientation="h",
        marker_color=colors, marker_line_width=0,
        opacity=0.9,
        hovertemplate="%{y}: %{x}<extra></extra>",
        text=tier_df["count"],
        textposition="outside",
        textfont=dict(family="DM Mono, monospace", size=9, color="#6B5A3E"),
    ))
    fig2.update_layout(**CHART_LAYOUT, height=260,
        xaxis=dict(**AXIS_STYLE, title="Positions"),
        yaxis=dict(
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(family="DM Mono, monospace", size=9, color="#6B5A3E"),
        ),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── chart row 2 — skill analysis ───────────────────────────────────────────────
st.markdown('<div class="lux-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Skill Intelligence</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2, gap="small")

with col3:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Acquisition Priorities</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Skills demanded by market · absent from profile</div>', unsafe_allow_html=True)

    missing_df = top_missing_skills(df, top_n=12)
    if not missing_df.empty:
        mdf = missing_df.sort_values("job_count")
        fig3 = go.Figure(go.Bar(
            x=mdf["job_count"], y=mdf["skill"],
            orientation="h",
            marker=dict(
                color=mdf["job_count"],
                colorscale=[[0, "#2A1A1A"], [0.5, AMBER], [1.0, GOLD]],
                line_width=0,
            ),
            opacity=0.95,
            hovertemplate="%{y}<br>%{x} positions<extra></extra>",
        ))
        fig3.update_layout(**CHART_LAYOUT, height=320,
            xaxis=dict(**AXIS_STYLE, title="Positions Requiring"),
            yaxis=dict(showgrid=False, zeroline=False, showline=False,
                       tickfont=dict(family="DM Mono, monospace", size=9, color="#6B5A3E")),
        )
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Competitive Strengths</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Profile skills resonating across matched positions</div>', unsafe_allow_html=True)

    matched_df = top_matched_skills(df, top_n=12)
    if not matched_df.empty:
        mdf2 = matched_df.sort_values("job_count")
        fig4 = go.Figure(go.Bar(
            x=mdf2["job_count"], y=mdf2["skill"],
            orientation="h",
            marker=dict(
                color=mdf2["job_count"],
                colorscale=[[0, "#1A2A1A"], [0.5, "#4A7A4A"], [1.0, "#7ABE7A"]],
                line_width=0,
            ),
            opacity=0.95,
            hovertemplate="%{y}<br>%{x} positions<extra></extra>",
        ))
        fig4.update_layout(**CHART_LAYOUT, height=320,
            xaxis=dict(**AXIS_STYLE, title="Positions Matching"),
            yaxis=dict(showgrid=False, zeroline=False, showline=False,
                       tickfont=dict(family="DM Mono, monospace", size=9, color="#6B5A3E")),
        )
        st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── leaderboard ────────────────────────────────────────────────────────────────
st.markdown('<div class="lux-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Position Leaderboard</div>', unsafe_allow_html=True)

st.markdown("""
<div style="font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:400;
            color:#D4C4A0;font-style:italic;margin-bottom:0.4rem;">
    Ranked by Semantic Match
</div>
<div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#3D3020;
            letter-spacing:0.15em;text-transform:uppercase;margin-bottom:2rem;">
    Positions ordered by AI cosine similarity score · Click to apply
</div>
""", unsafe_allow_html=True)

# header row
st.markdown("""
<div class="leaderboard-row leaderboard-header" style="background:transparent;">
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">#</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">Position</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">Location</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">Match</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">Tier</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#3D3020;text-transform:uppercase;">Apply</div>
</div>
""", unsafe_allow_html=True)

delays = ["delay-1","delay-2","delay-3","delay-4","delay-5"]
for i, row in df.head(20).iterrows():
    rank = list(df.index).index(i) + 1
    tc   = tier_class(row["match_tier"])
    bar  = min(row["match_score"], 100)
    remote_label = "Remote" if row["remote"] else row["location"].split(",")[0] if "," in str(row["location"]) else row["location"]
    delay = delays[min(rank - 1, 4)]
    apply_link = row.get("apply_url", "#") or "#"

    st.markdown(f"""
    <div class="leaderboard-row {delay}">
        <div class="lb-rank">{rank:02d}</div>
        <div>
            <div class="lb-title">{row['title']}</div>
            <div class="lb-company">{row['company'].upper()}</div>
        </div>
        <div class="lb-location">{remote_label}</div>
        <div class="lb-score-wrap">
            <div class="lb-score-num">{row['match_score']:.0f}%</div>
            <div class="lb-score-bar-bg">
                <div class="lb-score-bar" style="width:{bar}%"></div>
            </div>
        </div>
        <div><span class="lb-tier {tc}">{row['match_tier']}</span></div>
        <div><a href="{apply_link}" target="_blank" class="lb-apply">Apply →</a></div>
    </div>
    """, unsafe_allow_html=True)

# ── agent performance summary ──────────────────────────────────────────────────
st.markdown('<div class="lux-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Agent Intelligence Report</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="summary-grid">
    <div class="summary-card">
        <div class="summary-label">Median Score</div>
        <div class="summary-value">{metrics['median_match_score']}%</div>
        <div class="summary-caption">The 50th percentile match — how well a typical position aligns with the profile.</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Score Deviation</div>
        <div class="summary-value">{metrics['score_std']}%</div>
        <div class="summary-caption">Standard deviation across all matches. Lower values indicate a more consistent, reliable agent.</div>
    </div>
    <div class="summary-card">
        <div class="summary-label">Lead Employer</div>
        <div class="summary-value" style="font-size:1.3rem;margin-top:0.3rem;">{metrics['top_company']}</div>
        <div class="summary-caption">Most frequently appearing company across all matched positions in this dataset.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── footer ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:5rem;padding-top:2rem;border-top:1px solid #1A1510;
            display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:'Playfair Display',serif;font-size:1rem;color:#2A2018;
                letter-spacing:0.2em;">ORBIS</div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#2A2018;text-transform:uppercase;">
        Powered by sentence-transformers · all-MiniLM-L6-v2 · Streamlit
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:0.5rem;letter-spacing:0.2em;
                color:#2A2018;text-transform:uppercase;">Private Edition</div>
</div>
""", unsafe_allow_html=True)
