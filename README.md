# News-Scraper

## Scheduling / Running the scraper

This project exposes a small CLI runner at `backend/run_scraper.py` which you can use with cron or a scheduler. It handles DB connect/close and calls the scraper.

1) Cron (crontab)

Add a cron entry on your server to run the script at the desired interval. Example (run hourly):

```
# run every hour at minute 0, adjust paths as needed
0 * * * * /usr/bin/env python3 /home/hisoka/Projects/Reddit-Scraper/backend/run_scraper.py --type new --limit 500 --incremental true >> /var/log/reddit_scraper.log 2>&1
```

Make sure the environment variables for DB and Reddit API keys (CLIENT_ID, CLIENT_SECRET, USER_AGENT, etc.) are available to the cron job. You can load them in a wrapper script or set them in `/etc/environment`.

2) Apache Airflow

If you run Airflow, there's an example DAG at `airflow/dags/reddit_scraper_dag.py` that uses a PythonOperator to call the same runner. Place the `airflow/` directory in your Airflow DAGs folder or copy that single file to your configured `dags/` directory.

Notes for Airflow:
- Ensure the repository root is on `PYTHONPATH` so the DAG can import `backend.run_scraper`. You can do this by setting `export PYTHONPATH=/path/to/Reddit-Scraper` in the Airflow environment or by adjusting `sys.path` in the DAG (the example shows how).
- Install Airflow and required project dependencies in the same Python environment used by the scheduler and workers.

3) Development / manual run

You can run the scraper locally for testing:

```
python3 backend/run_scraper.py --type new --limit 50 --incremental true
```

4) Troubleshooting
- If imports fail in Airflow, add the repo to `PYTHONPATH` or use an absolute path in the DAG.
- Ensure env vars (Reddit credentials, DB URI) are visible to the scheduler and the worker processes.
