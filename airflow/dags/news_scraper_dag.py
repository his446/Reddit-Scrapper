# from backend.db.mongo import connect_db, close_db
from backend.services.scraper import run_news_api_scraper_job, run_reddit_scraper_job
from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

# Finding the Project ROOT
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import after sys is set

# Reddit Scraper for airflow to use
# def run_scraper_job(scrape_type="new", limit=100, incremental=True):
#     print("🚀 Starting RedditScraper job...")
#     connect_db()
#     try:
#         scraper = RedditScraper()
#         scraper.scrape(type=scrape_type, limit=limit, incremental=incremental)
#         print("✅ Scraping complete!")
#     except Exception as e:
#         print(f"❌ Scraper failed: {e}")
#         raise
#     finally:
#         close_db()
#         print("🛑 Database connection closed.")

# DAG default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# Definition
with DAG(
    dag_id="news_scraper_dag",
    default_args=default_args,
    description="Scrape AI-related Reddit posts, NewsApi articles and store them in MongoDB",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["reddit", "NewsApi", "ai", "scraper"],
) as dag:

    run_reddit_scraper_task = PythonOperator(
        task_id="run_reddit_scraper",
        python_callable=run_reddit_scraper_job,
        op_kwargs={
            "scrape_type": "new",
            "limit": 1000,
            "incremental": True,
        },
    )

    run_news_api_scraper_task = PythonOperator(
        task_id="run_news_api_scraper",
        python_callable=run_news_api_scraper_job,
        op_kwargs={
            "limit": 7000,
            "page_size": 100,
            "incremental": True,
        },
    )

    run_reddit_scraper_task, run_news_api_scraper_task
