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
        self.topics = [
            "AI", "artificial intelligence", "machine learning", "deep learning",
            "ChatGPT", "OpenAI", "neural network", "automation", "LLM",
            "generative AI", "autonomous systems"
        ]

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

                publishedAt_raw = art.get(
                    "published date") or art.get("publishedAt")
                publishedAt_dt = self.parse_datetime(
                    publishedAt_raw) or datetime.utcnow()

                # Skip old articles if incremental is on
                if incremental and last_timestamp and publishedAt_dt <= last_timestamp:
                    continue

                publisher = art.get("publisher") or {}
                source_name = publisher.get(
                    "title") or art.get("source") or "Unknown"
                source_id = publisher.get(
                    "href") or source_name.lower().replace(" ", "_")

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

        MAX_REQUESTS = 100  # Free-tier limit
        MAX_RESULTS = 10     # per request

        # Build ordered topic list
        requests = []
        for topic in self.topics:
            if len(requests) >= MAX_REQUESTS:
                break
            requests.append(topic)

        for idx, topic in enumerate(requests, start=1):
            if fetched_count >= limit:
                break

            print(f"📡 [{idx}/{len(requests)}] Fetching: {topic}")

            try:
                articles = self.client.get_news(topic)
            except Exception as e:
                print(f"❌ GNews request failed ({topic}): {e}")
                continue

            if not articles:
                continue

            for art in articles:
                if fetched_count >= limit:
                    break

                url = art.get("url")
                if not url:
                    continue

                # normalize published date
                published_raw = (
                    art.get("published date")
                    or art.get("publishedAt")
                    or None
                )
                try:
                    if published_raw:
                        publishedAt = datetime.strptime(
                            published_raw, "%a, %d %b %Y %H:%M:%S %Z"
                        )
                    else:
                        publishedAt = datetime.utcnow()
                except Exception:
                    publishedAt = datetime.utcnow()

                # incremental filtering
                if incremental and last_timestamp and publishedAt <= last_timestamp:
                    continue

                expanded_content = None
                if "[+" in str(art.get("content") or ""):
                    expanded_content = self.fetch_full_content(url)

                doc = {
                    "url": url,
                    "title": art.get("title"),
                    "author": art.get("author"),
                    "description": art.get("description"),
                    "content": art.get("content"),
                    "expanded_content": expanded_content,
                    "publishedAt": publishedAt,
                    "source_id": None,
                    "source_name": art.get("source"),
                    "saved_utc": datetime.utcnow(),
                }

                save_gnews_article(doc)
                fetched_count += 1

                if not newest_timestamp or publishedAt > newest_timestamp:
                    newest_timestamp = publishedAt

        if incremental and newest_timestamp and newest_timestamp != last_timestamp:
            update_last_gnews_timestamp(newest_timestamp)
            print(f"🔃 Updated GNews last timestamp: {newest_timestamp}")

        print(f"✅ Finished GNews scraping — {fetched_count} articles stored.")


def run_gnews_scraper_job(limit: int = 100, incremental: int = True):
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
