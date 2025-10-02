"""Orchestrator to run multiple scrapers, merge results, deduplicate and save to CSV.

Usage:
    python orchestrator.py --sources pipeline,jobspy --max-results 50
    python orchestrator.py --sources pipeline,jobspy --max-results 50 --csv data/internships.csv
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional
import pandas as pd

# Ensure project root is on sys.path so local packages can be imported
sys.path.insert(0, str(Path(__file__).parent))
# Also add JobSpy package folder if present (it contains the 'jobspy' package)
jobspy_dir = Path(__file__).parent / 'JobSpy'
if jobspy_dir.exists():
    sys.path.insert(0, str(jobspy_dir))

from models.internship import Internship, InternshipSchema, deduplicate_internships


logger = logging.getLogger('orchestrator')


def run_pipeline_scrapers(max_results: Optional[int] = None) -> List[Internship]:
    """Run the existing pipeline scrapers (Internshala, AICTE, Google STEP).
    This reuses the pipeline.run_scrapers() implementation if available.
    """
    try:
        import pipeline

        logger.info("Running pipeline scrapers...")
        return pipeline.run_scrapers(max_results_per_source=max_results)
    except Exception as e:
        logger.error(f"Failed to run pipeline scrapers: {e}")
        return []


def run_jobspy_scraper(max_results: Optional[int] = None) -> List[Internship]:
    """Run JobSpy and convert its DataFrame output into Internship objects.
    """
    import subprocess
    import csv

    logger.info("Running JobSpy scrapers (via JobSpy/main.py)...")

    jobspy_main = Path(__file__).parent / 'JobSpy' / 'main.py'
    jobs_csv = Path(__file__).parent / 'jobs.csv'

    # If the packaged jobspy.call works, we could call it directly. But some environments
    # have better success running the provided main.py script (you confirmed it works).
    if jobspy_main.exists():
        try:
            # Run JobSpy main.py which writes jobs.csv
            subprocess.run(['python', str(jobspy_main)], check=True)
            if not jobs_csv.exists():
                logger.error('JobSpy main.py did not produce jobs.csv')
                return []
            # Read jobs.csv
            df = pd.read_csv(jobs_csv)
        except subprocess.CalledProcessError as e:
            logger.error(f"JobSpy main.py failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to read jobs.csv: {e}")
            return []
    else:
        # Fallback: try importing jobspy.scrape_jobs directly
        try:
            import jobspy
            df = jobspy.scrape_jobs(
                site_name=["indeed", "google"],
                search_term="internship",
                results_wanted=max_results or 20,
                hours_old=72,
            )
        except Exception as e:
            logger.error(f"JobSpy scrape_jobs failed: {e}")
            return []

    if df is None or df.empty:
        logger.info("JobSpy returned no results")
        return []

    internships: List[Internship] = []
    for _, row in df.iterrows():
        title = row.get('title') or row.get('job') or row.get('job_title') or ''
        organization = row.get('company') or row.get('employer') or ''
        location = row.get('location') or row.get('display_location') or ''
        description = row.get('description') or ''
        application_link = row.get('job_url') or row.get('url') or row.get('posting_url') or ''
        stipend = row.get('min_amount') or row.get('salary') or row.get('stipend') or ''
        skills = row.get('skills') or row.get('tags') or ''

        # Normalize skills field into list
        skills_list = []
        if isinstance(skills, str):
            skills_list = [s.strip() for s in skills.split(',') if s.strip()]
        elif isinstance(skills, list):
            skills_list = skills

        internship = Internship(
            title=str(title),
            organization=str(organization),
            country="",
            location=str(location),
            description=str(description),
            application_link=str(application_link),
            stipend=str(stipend),
            skills_required=skills_list,
            source="JobSpy",
        )
        internships.append(internship)

    logger.info(f"Converted {len(internships)} JobSpy rows into Internship objects")
    return internships


def save_internships(internships: List[Internship], filename: str):
    """Save internships to CSV using InternshipSchema columns and write a small summary."""
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    if not internships:
        logger.warning("No internships to save")
        return

    data = [i.to_dict() for i in internships]
    df = pd.DataFrame(data)

    # Ensure columns exist and reorder
    schema = InternshipSchema()
    for col in schema.COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[schema.COLUMNS]

    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Saved {len(df)} internships to {filename}")

    # save summary
    summary_file = filename.replace('.csv', '_summary.txt')
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("INTERNSHIP SCRAPING SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Internships: {len(df)}\n")
        logger.info(f"Saved summary to {summary_file}")
    except Exception as e:
        logger.error(f"Failed to write summary: {e}")


def main():
    parser = argparse.ArgumentParser(description='Orchestrator for internships scrapers')
    parser.add_argument('--sources', default='pipeline,jobspy', help='Comma-separated sources: pipeline,jobspy')
    parser.add_argument('--max-results', type=int, default=50, help='Max results per source')
    parser.add_argument('--csv', default='data/internships.csv', help='Output CSV path')
    parser.add_argument('--dry-run', action='store_true', help='Run without writing CSV')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sources = [s.strip().lower() for s in args.sources.split(',') if s.strip()]
    all_internships: List[Internship] = []

    if 'pipeline' in sources:
        all_internships.extend(run_pipeline_scrapers(max_results=args.max_results))
    if 'jobspy' in sources:
        all_internships.extend(run_jobspy_scraper(max_results=args.max_results))

    logger.info(f"Total scraped internships before dedupe: {len(all_internships)}")
    unique = deduplicate_internships(all_internships)
    logger.info(f"After deduplication: {len(unique)} unique internships")

    if args.dry_run:
        for i, it in enumerate(unique[:10], 1):
            logger.info(f"{i}. {it.title} @ {it.organization} ({it.location}) [{it.source}]")
        return

    save_internships(unique, args.csv)


if __name__ == '__main__':
    main()
