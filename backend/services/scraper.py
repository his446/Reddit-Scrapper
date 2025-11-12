from newsapi import NewsApiClient
from datetime import datetime
import re
# from dotenv import load_dotenv
from backend.config import settings
import math
import praw
from typing import Literal
from newspaper import Article

from backend.db.mongo import close_db, connect_db, get_last_news_timestamp, get_last_reddit_timestamp, save_newsapi_article, save_post, update_last_news_timestamp, update_last_reddit_timestamp
# load_dotenv()
# client_id=os.getenv("CLIENT_ID", "")
# client_secret=os.getenv("CLIENT_SECRET", "")
# user_agent=os.getenv("USER_AGENT", "")


class Scraper(object):
    def __init__(self):
        self.TARGET_SUBS = settings.TARGET_SUBS.split("+")
        self.KEYWORDS = settings.KEYWORDS.split("+")
        self.FALSE_POSITIVES = ["ukrain", "russia", "war", "politics"]

    def text_contains_ai(self, text: str) -> bool:
        """Check if text contains AI keywords, handling short keywords correctly."""
        if not text:
            return False
        text = text.lower()

        for kw in self.KEYWORDS:
            kw = kw.lower().strip()
            if len(kw) <= 2:  # short keywords: ai, ml
                pattern = rf"\b{re.escape(kw)}\b|\b{re.escape(kw)}-(?=\w)"
            else:  # longer keywords/phrases
                pattern = rf"\b{re.escape(kw)}\b"

            if re.search(pattern, text):
                return True
        return False


class RedditScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.user_agent = settings.USER_AGENT
        self.praw = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
        self.reddit_fields = [
            "id", "title", "author", "subreddit", "score", "upvote_ratio",
            "num_comments", "created_utc", "url", "permalink", "selftext"
        ]

    def post_mentions_ai(self, post: praw.reddit.Submission) -> bool:
        """Return True if post is AI-related and not a false positive."""
        text = (post.title or "") + " " + (getattr(post, "selftext", "") or "")
        text_lower = text.lower()

        # Must contain AI keyword
        if not self.text_contains_ai(text_lower):
            return False

        # Check false-positive terms
        for fp in self.FALSE_POSITIVES:
            if fp in text_lower:
                # Split into sentences, keep only if AI keyword exists in same sentence
                sentences = re.split(r"[.!?]", text_lower)
                for sentence in sentences:
                    if fp in sentence and not self.text_contains_ai(sentence):
                        return False  # discard if no AI mention in same sentence
        return True

    def extract_post_data(self, post: praw.reddit.Submission) -> dict:
        data = {}
        for field in self.reddit_fields:
            value = getattr(post, field, None)

            if field == "author":
                value = value.name if value else "unknown"
            elif field == "subreddit":
                value = value.display_name if value else "unknown"
            elif field == "created_utc":
                value = datetime.fromtimestamp(
                    post.created_utc) if value else datetime.now()
            data[field] = value

        if "permalink" in data and data["permalink"]:
            data["permalink"] = f"https://reddit.com{data['permalink']}"

        return data

    def scrape(self, type: Literal["top", "hot", "new", "rising"] = "new", limit: int = 25, incremental: bool = True):
        total_saved_posts = 0
        for sub in self.TARGET_SUBS:
            subreddit = self.praw.subreddit(sub)
            last_created_utc = get_last_reddit_timestamp(sub)
            new_last_created_utc = last_created_utc

            if type == "top":
                posts = subreddit.top(limit=limit)
            elif type == "hot":
                posts = subreddit.hot(limit=limit)
            elif type == "new":
                posts = subreddit.new(limit=limit)
            elif type == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Unsupported Scraping Type: {type}")
            new_posts_count = 0
            for post in posts:

                if incremental and post.created_utc <= last_created_utc:
                    continue

                if self.post_mentions_ai(post):
                    doc = self.extract_post_data(post)
                    save_post(doc)
                    new_posts_count += 1
                    print(f"✅ Saved post: {post.title[:60]}")

                    if post.created_utc > new_last_created_utc:
                        new_last_created_utc = post.created_utc

            if incremental:
                update_last_reddit_timestamp(sub, new_last_created_utc)
                print(
                    f"🔃 Updated timestamp for r/{sub}: {new_last_created_utc}")
            print(f"📊 Finished r/{sub}: {new_posts_count} posts saved.")
            total_saved_posts += new_posts_count
        print(f"🏁 Finished {", ".join([f"r/{sub}" for sub in self.TARGET_SUBS])}: {
              total_saved_posts} posts saved.")


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

        # Calculate total pages needed to respect `limit` and `page_size`
        total_pages = math.ceil(limit / page_size)
        fetched_count = 0
        newest_timestamp = last_timestamp

        for page in range(1, total_pages + 1):
            params = {
                'q': self.query,
                'language': 'en',
                'sort_by': 'publishedAt',
                'page_size': min(page_size, limit - fetched_count),
                'page': page
            }
            if incremental and last_timestamp:
                params["from_param"] = last_timestamp

            try:
                res = self.client.get_everything(**params)
            except Exception as e:
                print(f"❌ Failed Scraping NewsAPI page {page}: {e}")
                break

            if res["status"] != 'ok' or not res["articles"]:
                break

            for art in res['articles']:
                if fetched_count >= limit:
                    break  # stop if we reached the limit

                url = art.get("url")
                if not url:
                    continue

                api_content = art.get("content")
                expanded_content = None
                if api_content and "[+" in api_content:
                    expanded_content = self.fetch_full_content(url)

                doc = {
                    "url": url,
                    "title": art["title"],
                    "author": art.get("author"),
                    "description": art.get("description"),
                    "content": api_content,
                    "expanded_content": expanded_content,
                    "publishedAt": art["publishedAt"],
                    "source_id": art["source"]["id"] if art["source"] else None,
                    "source_name": art["source"]["name"] if art["source"] else None,
                    "saved_utc": datetime.now(),
                }

                save_newsapi_article(doc)
                fetched_count += 1

                # Track newest timestamp for incremental updates
                article_ts = art["publishedAt"]
                if not newest_timestamp or article_ts > newest_timestamp:
                    newest_timestamp = article_ts

            if fetched_count >= limit:
                break

        # Update last timestamp if incremental
        if incremental and newest_timestamp and newest_timestamp != last_timestamp:
            update_last_news_timestamp(newest_timestamp)
            print(f"🔃 Updated NewsAPI last timestamp: {newest_timestamp}")


def run_reddit_scraper_job(scrape_type: Literal["top", "hot", "new", "rising"] = "new", limit: int = 100, incremental: bool = True):
    """Wrapper to be used by Airflow DAG."""
    print("🚀 Starting RedditScraper job...")
    connect_db()
    try:
        scraper = RedditScraper()
        scraper.scrape(type=scrape_type, limit=limit, incremental=incremental)
        print("✅ Reddit Scraping complete!")
    except Exception as e:
        print(f"❌ Scraper failed: {e}")
        raise
    finally:
        close_db()
        print("🛑 Reddit Database connection closed.")


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


# if __name__ == "__main__":
#     NS = NewsApiScrapper()
#     NS.scrape_news(limit=5)
