from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator  # <-- standard provider is fine

# Dynamically find project root (where backend/ lives)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ✅ Import after sys.path is set
from backend.services.scraper import RedditScraper
from backend.db.mongo import connect_db, close_db

# 🧠 Define a wrapper for Airflow
def run_scraper_job(scrape_type="new", limit=100, incremental=True, **context):
    print("🚀 Starting RedditScraper job...")
    connect_db()
    try:
        scraper = RedditScraper()
        scraper.scrape(type=scrape_type, limit=limit, incremental=incremental)
        print("✅ Scraping complete!")
    except Exception as e:
        print(f"❌ Scraper failed: {e}")
        raise
    finally:
        close_db()
        print("🛑 Database connection closed.")

# 🧱 DAG defaults
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# 🕓 DAG definition
with DAG(
    dag_id="reddit_scraper_dag",
    default_args=default_args,
    description="Scrape AI-related Reddit posts and store them in MongoDB",
    schedule="0 */12 * * *",  # every 12 hours scraping
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["reddit", "ai", "scraper"],
) as dag:

    run_scraper_task = PythonOperator(
        task_id="run_reddit_scraper",
        python_callable=run_scraper_job,
        op_kwargs={
            "scrape_type": "new",
            "limit": 1000,
            "incremental": True,
        },
    )

    run_scraper_task
