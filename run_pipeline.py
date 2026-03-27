"""
run_pipeline.py — End-to-end runner.

Usage:
    # Live jobs via Apify:
    export APIFY_TOKEN=your_token_here
    python run_pipeline.py

    # Sample data (no API key needed):
    python run_pipeline.py --sample
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, "src")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample", action="store_true",
        help="Use sample data instead of live Apify fetch"
    )
    parser.add_argument(
        "--no-dashboard", action="store_true",
        help="Run pipeline without launching Streamlit"
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  AI Job Match Quality Analyzer — Pipeline Runner")
    print("=" * 55)

    if args.sample:
        print("\n[1/1] Generating sample data...")
        from generate_sample_data import generate_jobs
        import pandas as pd
        os.makedirs("data", exist_ok=True)
        jobs = generate_jobs(35)
        pd.DataFrame(jobs).to_csv("data/sample_results.csv", index=False)
        print("  Sample data ready -> data/sample_results.csv")
    else:
        print("\n[1/2] Fetching live jobs from LinkedIn via Apify...")
        from fetch_jobs import fetch_jobs, save_jobs
        jobs = fetch_jobs(limit=30)
        save_jobs(jobs)

        print("\n[2/2] Running ML matching engine...")
        from matcher import run_matching, save_results
        df = run_matching()
        save_results(df, "data/match_results.csv")
        print(f"  Scored {len(df)} jobs.")

    if not args.no_dashboard:
        print("\n[Final] Launching Streamlit dashboard...")
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run",
             "dashboard/app.py", "--server.port", "8501"],
            check=True,
        )


if __name__ == "__main__":
    main()
