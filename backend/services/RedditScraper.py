from newsapi import NewsApiClient
from datetime import datetime
import re
from backend.config import settings
import praw
from typing import Literal

from backend.db.mongo import close_db, connect_db, get_last_reddit_timestamp, save_post, update_last_reddit_timestamp

class RedditScraper(object):
    def __init__(self):
        self.TARGET_SUBS = settings.TARGET_SUBS.split("+")
        self.KEYWORDS = settings.KEYWORDS.split("+")
        self.FALSE_POSITIVES = ["ukrain", "russia", "war", "politics"]

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
