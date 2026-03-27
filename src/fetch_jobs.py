"""
fetch_jobs.py
Pulls live job postings from LinkedIn via Apify's LinkedIn Jobs Scraper.
Saves raw results to data/raw_jobs.json
"""

import os
import json
import time
import requests
from datetime import datetime

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

# LinkedIn search URLs targeting ML/AI/Data Analyst entry-level roles
SEARCH_URLS = [
    "https://www.linkedin.com/jobs/search/?keywords=machine+learning+engineer+new+grad&f_E=1,2&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search/?keywords=data+analyst+entry+level+AI&f_E=1,2&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search/?keywords=AI+engineer+new+grad&f_E=1,2&position=1&pageNum=0",
]


def fetch_jobs(limit: int = 30) -> list:
    """Call Apify LinkedIn Jobs Scraper and return raw job list."""
    if not APIFY_TOKEN:
        raise ValueError(
            "APIFY_TOKEN not set. Export it: export APIFY_TOKEN=your_token"
        )

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Apify actor run...")

    run_url = "https://api.apify.com/v2/acts/curious_coder~linkedin-jobs-scraper/runs"
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "urls": SEARCH_URLS,
        "count": limit,
        "scrapeCompany": False,
    }

    response = requests.post(run_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    run_data = response.json()["data"]
    run_id = run_data["id"]
    dataset_id = run_data["defaultDatasetId"]

    print(f"  Actor run started. Run ID: {run_id}")
    print("  Waiting for results...")

    # Poll until finished (max 5 min)
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    for _ in range(60):
        time.sleep(5)
        status_resp = requests.get(status_url, headers=headers, timeout=15)
        status = status_resp.json()["data"]["status"]
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Actor run failed with status: {status}")

    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?limit={limit}"
    items_resp = requests.get(dataset_url, headers=headers, timeout=30)
    items_resp.raise_for_status()
    jobs = items_resp.json()

    print(f"  Fetched {len(jobs)} jobs.")
    return jobs


def save_jobs(jobs: list, path: str = "data/raw_jobs.json") -> None:
    os.makedirs("data", exist_ok=True)
    with open(path, "w") as f:
        json.dump(jobs, f, indent=2, default=str)
    print(f"  Saved to {path}")


if __name__ == "__main__":
    jobs = fetch_jobs(limit=30)
    save_jobs(jobs)
