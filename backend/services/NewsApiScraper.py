from newsapi import NewsApiClient
from datetime import datetime
from backend.config import settings
import math
from newspaper import Article

from backend.db.mongo import close_db, connect_db, get_last_news_timestamp, save_newsapi_article, update_last_news_timestamp


class NewsApiScrapper(object):
    def __init__(self):
        self.client = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self.query = (
            '"AI" OR "artificial intelligence" OR "ChatGPT" OR "OpenAI" '
            'OR "machine learning" OR "GPT" OR "automation" OR "deep learning" '
            'OR "neural network" OR "LLM" OR "generative AI"'
        )

    def fetch_full_content(self, url: str) -> str | None:
        try:
            article = Article(url, language="en")
            article.download()
            article.parse()

            text = article.text.strip()
            return text if text else None
        except Exception:
            return None

    def scrape_news(self, limit: int = 100, page_size: int = 100, incremental: bool = True):
        last_timestamp = get_last_news_timestamp() if incremental else None

        # Convert last_timestamp to the proper NewsAPI format
        from_param = None
        if incremental and last_timestamp:
            from_param = last_timestamp.strip()
            if from_param.endswith("Z"):
                from_param = from_param[:-1]  # remove trailing Z 
        total_pages = math.ceil(limit / page_size)
        fetched_count = 0
        newest_timestamp = last_timestamp

        for page in range(1, total_pages + 1):
            params = {
                "q": self.query,
                "language": "en",
                "sort_by": "publishedAt",
                "page_size": min(page_size, limit - fetched_count),
                "page": page,
            }
            if incremental and from_param:
                params["from_param"] = from_param

            try:
                res = self.client.get_everything(**params)
                print(f"Total article results: {res.get("totalResults")}")
            except Exception as e:
                print(f"❌ Failed Scraping NewsAPI page {page}: {e}")
                break

            if res.get("status") != "ok" or not res.get("articles"):
                print(f"⚠️ No articles found or bad response on page {page}.")
                break

            for art in res["articles"]:
                if fetched_count >= limit:
                    break

                url = art.get("url")
                if not url:
                    continue

                api_content = art.get("content")
                expanded_content = None
                if api_content and "[+" in api_content:
                    expanded_content = self.fetch_full_content(url)

                doc = {
                    "url": url,
                    "title": art.get("title"),
                    "author": art.get("author"),
                    "description": art.get("description"),
                    "content": api_content,
                    "expanded_content": expanded_content,
                    "publishedAt": art.get("publishedAt"),
                    "source_id": art.get("source", {}).get("id"),
                    "source_name": art.get("source", {}).get("name"),
                    "saved_utc": datetime.utcnow(),
                }

                save_newsapi_article(doc)
                fetched_count += 1

                # Track newest timestamp
                article_ts_str = art.get("publishedAt")
                if article_ts_str:
                    try:
                        article_dt = datetime.fromisoformat(article_ts_str.replace("Z", "+00:00"))
                        article_ts = article_dt.timestamp()
                        if not newest_timestamp or article_ts > newest_timestamp:
                            newest_timestamp = article_ts
                    except Exception:
                        pass

            if fetched_count >= limit:
                break

        # Update incremental timestamp
        if incremental and newest_timestamp and newest_timestamp != last_timestamp:
            update_last_news_timestamp(newest_timestamp)
            print(f"🔃 Updated NewsAPI last timestamp: {newest_timestamp}")


def run_news_api_scraper_job(limit: int = 100, page_size: int = 100, incremental:int = True):
    """Wrapper to be used by Airflow DAG."""
    print("🚀 Starting NewsApi Scraper job...")
    connect_db()
    try:
        NS = NewsApiScrapper()
        NS.scrape_news(limit=limit, page_size=page_size, incremental=incremental)
        print("✅ NewsAPI Scraping complete!")
    except Exception as e:
        print(f"❌ NewsAPI Scraper failed: {e}")
        raise
    finally:
        close_db()
        print("🛑 Database connection closed.")
