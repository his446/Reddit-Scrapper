#!/usr/bin/env python3
"""Small CLI wrapper to run the Reddit scraper from cron or other schedulers.

This script connects to the MongoDB, runs the scraper, and closes the DB.
Use it from cron or from an Airflow PythonOperator by importing `run`.
"""
import argparse
from backend.db.mongo import connect_db, close_db
from backend.services.scraper import RedditScraper


def run(scrape_type: str = "new", limit: int = 25, incremental: bool = True) -> None:
    """Run the Reddit scraper with the provided options.

    Args:
        scrape_type: one of ('top','hot','new','rising')
        limit: number of posts to fetch per subreddit
        incremental: whether to use incremental timestamps
    """
    connect_db()
    try:
        scraper = RedditScraper()
        scraper.scrape(type=scrape_type, limit=limit, incremental=incremental)
    finally:
        close_db()


def _parse_bool(v: str) -> bool:
    return v.lower() in ("1", "true", "t", "yes", "y")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Reddit scraper")
    parser.add_argument("--type", default="new", help="scrape type: top|hot|new|rising")
    parser.add_argument("--limit", type=int, default=25, help="limit posts per subreddit")
    parser.add_argument("--incremental", default="true", help="incremental: true/false")
    args = parser.parse_args()

    run(scrape_type=args.type, limit=args.limit, incremental=_parse_bool(args.incremental))


if __name__ == "__main__":
    main()
