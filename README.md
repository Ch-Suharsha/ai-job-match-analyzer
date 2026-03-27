# 🎯 AI Job Match Quality Analyzer

> An NLP-powered agent performance dashboard that scores live job postings against a candidate profile, surfaces skill gaps, and tracks matching quality metrics — built to mirror the data layer of a real AI job search agent.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![ML](https://img.shields.io/badge/ML-sentence--transformers-orange)](https://sbert.net)

---

## What This Does

Jobright.ai's core product is an AI agent that matches job seekers to roles. This project analyzes **how well that matching works** by:

1. **Pulling live job postings** from LinkedIn via Apify
2. **Embedding both the candidate profile and job descriptions** using `all-MiniLM-L6-v2` (384-dim sentence embeddings)
3. **Computing cosine similarity scores** between the candidate and each job
4. **Running a skill gap analysis** — what does the market want vs. what does the candidate have?
5. **Displaying everything** in an interactive Streamlit dashboard with KPIs, charts, and a ranked leaderboard

This is exactly what a data analyst at an AI job search company would build to help the product team improve agent performance.

---

## How It Works

```
Candidate Profile (JSON)
        +
Live Job Postings (Apify → LinkedIn)
        ↓
Text Embedding (all-MiniLM-L6-v2, 384 dimensions)
        ↓
Cosine Similarity Score per Job (0–100%)
        ↓
Skill Gap Analysis (matched vs. missing skills)
        ↓
Streamlit Dashboard
   ├── KPI cards (avg score, strong matches, remote %)
   ├── Match score distribution histogram
   ├── Tier breakdown bar chart
   ├── Skill gap chart (missing skills = upskilling targets)
   ├── Matched skills chart (strongest competitive assets)
   └── Job leaderboard with apply links
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Ch-Suharsha/ai-job-match-analyzer.git
cd ai-job-match-analyzer
pip install -r requirements.txt
```

### 2A. Run with Sample Data (no API key needed)

```bash
python run_pipeline.py --sample
```

Generates 35 realistic synthetic jobs and launches the dashboard instantly.

### 2B. Run with Live Data (requires Apify token)

```bash
export APIFY_TOKEN=your_apify_token_here
python run_pipeline.py
```

Fetches real live job postings from LinkedIn, scores them, and launches the dashboard.

### 3. Dashboard opens at `http://localhost:8501`

---

## Project Structure

```
ai-job-match-analyzer/
├── candidate_profile.json       ← Candidate skills, bio, target roles
├── run_pipeline.py              ← End-to-end runner (fetch → score → dashboard)
├── requirements.txt
│
├── src/
│   ├── fetch_jobs.py            ← Apify LinkedIn scraper integration
│   ├── matcher.py               ← Core ML engine (embeddings + cosine similarity)
│   ├── gap_analysis.py          ← Skill gap + agent performance metrics
│   └── generate_sample_data.py  ← Synthetic data generator (no API key needed)
│
├── dashboard/
│   └── app.py                   ← Streamlit dashboard
│
└── data/                        ← Generated at runtime
    ├── raw_jobs.json            ← Raw Apify output
    ├── match_results.csv        ← Scored + ranked jobs
    └── sample_results.csv       ← Sample data for demo
```

---

## ML Architecture

**Model:** `all-MiniLM-L6-v2` from sentence-transformers (384-dim, CPU-optimized)

```python
profile_embedding = model.encode([profile_text])       # 1 × 384
job_embedding     = model.encode([job_description])    # 1 × 384
score = cosine_similarity(profile_embedding, job_embedding)  # scalar 0–1
```

**Match Tiers:**

| Score | Tier |
|---|---|
| ≥ 75% | 🟢 Strong Match |
| 60–74% | 🔵 Good Match |
| 45–59% | 🟡 Partial Match |
| < 45% | 🔴 Low Match |

---

## Agent Performance Metrics

| Metric | What It Tells You |
|---|---|
| Avg Match Score | Overall quality of agent recommendations |
| High Quality Rate | % of jobs that are Strong or Good matches |
| Score Std Dev | Consistency of matching — lower is better |
| Remote Job % | What fraction of matches are remote-eligible |
| Skill Gap Distribution | What to learn next to increase match scores |

---

## Tech Stack

| Tool | Role |
|---|---|
| `sentence-transformers` | NLP embeddings (all-MiniLM-L6-v2) |
| `scikit-learn` | Cosine similarity computation |
| `pandas` | Data wrangling and analysis |
| `Apify` | Live LinkedIn job scraping |
| `Streamlit` | Interactive dashboard |
| `Plotly` | Charts and visualizations |

---

## Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Point to `dashboard/app.py`
4. Add `APIFY_TOKEN` to secrets (optional — works with sample data too)

---

*Built to demonstrate data analyst + ML skills for AI agent products.*
