from email.utils import parsedate_to_datetime
from gnews import GNews
from datetime import datetime, timedelta
from newspaper import Article
import math

from backend.db.mongo import close_db, connect_db, get_last_gnews_timestamp, save_gnews_article, update_last_gnews_timestamp

# class GnewsScraper(object):

#     def __init__(self, query: str = None, api_key: str = None):
#         self.query = query or (
#             "AI OR \"artificial intelligence\" OR ChatGPT OR OpenAI "
#             "OR \"machine learning\" OR GPT OR automation OR \"deep learning\" "
#             "OR \"neural network\" OR LLM OR \"generative AI\""
#         )
#         # Initialize GNews client
#         self.client = GNews(language='en', max_results=10, period='30d', api_key=api_key)
        
#     def fetch_full_content(self, url: str) -> str | None:
#         try:
#             article = Article(url, language="en")
#             article.download()
#             article.parse()

#             text = article.text.strip()
#             return text if text else None
#         except Exception:
#             return None

#     def scrape_news(self, limit: int = 100, incremental: bool = True):
#         last_timestamp = get_last_gnews_timestamp() if incremental else None

#         # Calculate max pages respecting the API limits
#         max_articles_per_request = 10  # per free-tier spec
#         total_requests = min(math.ceil(limit / max_articles_per_request), 100)  # max 100 requests/day

#         fetched_count = 0
#         newest_timestamp = last_timestamp

#         for request_num in range(total_requests):
#             try:
#                 articles = self.client.get_news(self.query)
#             except Exception as e:
#                 print(f"❌ Failed GNews request {request_num + 1}: {e}")
#                 break

#             if not articles:
#                 break

#             for art in articles:
#                 if fetched_count >= limit:
#                     break

#                 url = art.get("url")
#                 if not url:
#                     continue

#                 publishedAt = art.get("published date") or art.get("publishedAt") or datetime.utcnow().isoformat()
#                 doc = {
#                     "url": url,
#                     "title": art.get("title"),
#                     "author": art.get("author"),
#                     "description": art.get("description"),
#                     "content": art.get("content"),
#                     "expanded_content": None,  # Optional: can use fetch_full_content(url)
#                     "publishedAt": publishedAt,
#                     "source_name": art.get("source"),
#                     "saved_utc": datetime.now(),
#                 }

#                 save_gnews_article(doc)
#                 fetched_count += 1

#                 if not newest_timestamp or publishedAt > newest_timestamp:
#                     newest_timestamp = publishedAt

#             if fetched_count >= limit:
#                 break

#         if incremental and newest_timestamp and newest_timestamp != last_timestamp:
#             update_last_gnews_timestamp(newest_timestamp)
#             print(f"🔃 Updated GNews last timestamp: {newest_timestamp}")


class GnewsScraper:
    def __init__(self, query: str = None):
        self.query = query or (
            'AI OR "artificial intelligence" OR ChatGPT OR OpenAI '
            'OR "machine learning" OR GPT OR automation OR "deep learning" '
            'OR "neural network" OR LLM OR "generative AI"'
        )
        self.client = GNews(language="en", max_results=10, period="30d")

    def fetch_full_content(self, url: str) -> str | None:
        """Attempt to extract full article text using newspaper3k."""
        try:
            article = Article(url, language="en")
            article.download()
            article.parse()
            text = article.text.strip()
            return text if text else None
        except Exception:
            return None
        
    def parse_datetime(self, date_str: str) -> datetime | None:
        """Handle multiple possible GNews date formats."""
        if not date_str:
            return None
        try:
            # Example: "Sat, 08 Nov 2025 09:00:00 GMT"
            return parsedate_to_datetime(date_str)
        except Exception:
            try:
                return datetime.fromisoformat(date_str.replace("Z", ""))
            except Exception:
                return None

    def scrape_news_old(self, limit: int = 100, incremental: bool = True):
        last_timestamp = get_last_gnews_timestamp() if incremental else None
        max_articles_per_request = 10
        total_requests = min(math.ceil(limit / max_articles_per_request), 100)

        fetched_count = 0
        newest_timestamp = last_timestamp

        for request_num in range(total_requests):
            try:
                articles = self.client.get_news(self.query)
            except Exception as e:
                print(f"❌ Failed GNews request {request_num + 1}: {e}")
                break

            if not articles:
                break

            for art in articles:
                if fetched_count >= limit:
                    break

                url = art.get("url")
                if not url:
                    continue

                publishedAt_raw = art.get("published date") or art.get("publishedAt")
                publishedAt_dt = self.parse_datetime(publishedAt_raw) or datetime.utcnow()

                # Skip old articles if incremental is on
                if incremental and last_timestamp and publishedAt_dt <= last_timestamp:
                    continue

                publisher = art.get("publisher") or {}
                source_name = publisher.get("title") or art.get("source") or "Unknown"
                source_id = publisher.get("href") or source_name.lower().replace(" ", "_")

                expanded_content = self.fetch_full_content(url)

                doc = {
                    "url": url,
                    "title": art.get("title"),
                    "author": art.get("author"),
                    "description": art.get("description"),
                    "content": art.get("content"),
                    "expanded_content": expanded_content,
                    "publishedAt": publishedAt_dt,
                    "source_id": source_id,
                    "source_name": source_name,
                    "saved_utc": datetime.now(),
                }

                try:
                    save_gnews_article(doc)
                    fetched_count += 1
                except Exception as e:
                    print(f"❌ Failed to save article {url}: {e}")
                    continue

                if not newest_timestamp or publishedAt_dt > newest_timestamp:
                    newest_timestamp = publishedAt_dt

            if fetched_count >= limit:
                break

        if incremental and newest_timestamp and newest_timestamp != last_timestamp:
            update_last_gnews_timestamp(newest_timestamp)
            print(f"🔃 Updated GNews last timestamp: {newest_timestamp}")

        print(f"✅ GNews scraping complete — {fetched_count} articles saved.")
    
    def scrape_news(self, limit: int = 100, incremental: bool = True):
        last_timestamp = get_last_gnews_timestamp() if incremental else None
        newest_timestamp = last_timestamp
        fetched_count = 0

        # ⚙️ Configuration
        max_results_per_req = 10
        max_requests_per_day = 100

        # Derive date windows (e.g., 5-day slices up to 30 days back)
        days_back = 30
        window_days = 5
        date_windows = []
        today = datetime.now()

        for i in range(0, days_back, window_days):
            end = today - timedelta(days=i)
            start = end - timedelta(days=window_days)
            date_windows.append((start, end))

        # Merge topics × date windows until we hit the request limit
        requests = []
        for topic in self.topics:
            for start, end in date_windows:
                if len(requests) >= max_requests_per_day:
                    break
                requests.append((topic, start, end))
            if len(requests) >= max_requests_per_day:
                break

        # 📰 Fetch data
        for i, (topic, start, end) in enumerate(requests, start=1):
            if fetched_count >= limit:
                break

            from_str = start.strftime("%Y-%m-%dT00:00:00Z")
            to_str = end.strftime("%Y-%m-%dT23:59:59Z")

            try:
                print(f"📡 [{i}/{len(requests)}] Fetching topic '{topic}' ({from_str} → {to_str})")
                articles = self.client.get_news(topic, from_=from_str, to_=to_str)
            except Exception as e:
                print(f"❌ Failed GNews request {i}: {e}")
                continue

            if not articles:
                continue

            for art in articles:
                if fetched_count >= limit:
                    break

                url = art.get("url")
                if not url:
                    continue

                publishedAt_raw = art.get("published date") or art.get("publishedAt")
                publishedAt_dt = self.parse_datetime(publishedAt_raw) or datetime.now()

                expanded_content = self.fetch_full_content(url) if "[+" in str(art.get("content") or "") else None

                doc = {
                    "url": url,
                    "title": art.get("title"),
                    "author": art.get("author"),
                    "description": art.get("description"),
                    "content": art.get("content"),
                    "expanded_content": expanded_content,
                    "publishedAt": publishedAt_dt,
                    "source_id": None,
                    "source_name": art.get("source"),
                    "saved_utc": datetime.now(),
                }

                save_gnews_article(doc)
                fetched_count += 1

                if not newest_timestamp or publishedAt_dt > newest_timestamp:
                    newest_timestamp = publishedAt_dt

        if incremental and newest_timestamp and newest_timestamp != last_timestamp:
            update_last_gnews_timestamp(newest_timestamp)
            print(f"🔃 Updated GNews last timestamp: {newest_timestamp}")
                    
def run_gnews_scraper_job(limit: int = 100, incremental:int = True):
    """Wrapper to be used by Airflow DAG."""
    print("🚀 Starting Gnews Scraper job...")
    connect_db()
    try:
        GS = GnewsScraper()
        GS.scrape_news(limit=limit, incremental=incremental)
        print("✅ Gnews Scraping complete!")
    except Exception as e:
        print(f"❌ Gnews Scraper failed: {e}")
        raise
    finally:
        close_db()
        print("🛑 Database connection closed.")