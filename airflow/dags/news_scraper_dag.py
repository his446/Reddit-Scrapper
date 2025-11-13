# from backend.db.mongo import connect_db, close_db
from backend.services.GnewsScraper import run_gnews_scraper_job
from backend.services.NewsApiScraper import run_news_api_scraper_job
from backend.services.RedditScraper import run_reddit_scraper_job
from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

# Finding the Project ROOT
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
            "limit": 100,
            "page_size": 100,
            "incremental": True,
        },
    )
    
    run_gnews_scraper_task = PythonOperator(
        task_id="run_gnews_scraper",
        python_callable=run_gnews_scraper_job,
        op_kwargs={
            "limit": 900,
            "incremental": True,
        },
    )

    run_reddit_scraper_task, run_news_api_scraper_task, run_gnews_scraper_task
