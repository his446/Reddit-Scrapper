import asyncio
from datetime import datetime
import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

from backend.models.NewsArticleModel import NewsArticleModel
from backend.models.RedditPostModel import RedditPost
from backend.models.GnewsArticleModel import GnewsArticleModel

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "news")

# Create the client & db at module load
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def connect_db():
    """Initialize MongoDB indexes (id for posts, url for articles)."""
    db.reddit_posts.create_index([("id", ASCENDING)], unique=True, sparse=True)
    db.newsapi_articles.create_index([("url", ASCENDING)], unique=True, sparse=True)
    db.gnews_articles.create_index([("url", ASCENDING)], unique=True, sparse=True)
    db.scrape_meta.create_index(
        [("subreddit", ASCENDING)], unique=True, sparse=True)
    print("✅ Connected to MongoDB!")


def close_db():
    """Close MongoDB client connection."""
    client.close()
    print("🛑 Closed MongoDB connection!")


def save_post(raw_data: dict):
    """save or update a Reddit post."""
    if "created_utc" not in raw_data:
        raw_data["created_utc"] = datetime.now()
    if "saved_utc" not in raw_data:
        raw_data["saved_utc"] = datetime.now()

    try:
        post = RedditPost(**raw_data)
        db.reddit_posts.update_one(
            {"id": post.id},
            {"$set": post.model_dump(mode="json")},
            upsert=True,
        )
        print(f"✅ Saved post: {post.title[:80]}")
    except Exception as e:
        print(f"❌ Failed to save Reddit post {raw_data.get('id')}: {e}")

def save_newsapi_article(raw_data: dict):
    """save or update a NewsApi Article."""
    
    try:
        art = NewsArticleModel(**raw_data)
        db.newsapi_articles.update_one(
            {"url": str(art.url)},
            {"$set": art.model_dump(mode="json")},
            upsert=True,
        )
        print(f"✅ Saved article: {art.title[:80]}")
    except Exception as e:
        print(f"❌ Failed to save article  {raw_data.get('url')}: {e}")
        
def save_gnews_article(raw_data: dict):
    """save or update a Gnews Article."""
    
    try:
        art = GnewsArticleModel(**raw_data)
        db.gnews_articles.update_one(
            {"url": str(art.url)},
            {"$set": art.model_dump(mode="json")},
            upsert=True,
        )
        print(f"✅ Saved article: {art.title[:80]}")
    except Exception as e:
        print(f"❌ Failed to save article  {raw_data.get('url')}: {e}")
        
def get_last_reddit_timestamp(subreddit: str) -> float:
    """"Return the last created_utc timestamp for a subreddit."""
    record = db.scrape_meta.find_one({"subreddit": subreddit})
    return record["last_created_utc"] if record else 0.0


def update_last_reddit_timestamp(subreddit: str, timestamp: float | datetime):
    """Update the last fetched timestamp for a subreddit."""
    if isinstance(timestamp, datetime):
        timestamp = timestamp.timestamp()
    db.scrape_meta.update_one(
        {"subreddit": subreddit},
        {"$set": {"last_created_utc": timestamp}},
        upsert=True
    )

def get_last_news_timestamp() -> str | None:
    """Return the last publishedAt timestamp for NewsAPI scraper."""
    record = db.scrape_meta.find_one({"source": "newsapi"})
    return record["last_published_at"] if record else None


def update_last_news_timestamp(timestamp: str):
    """Update the last fetched timestamp for NewsAPI scraper."""
    db.scrape_meta.update_one(
        {"source": "newsapi"},
        {"$set": {"last_published_at": timestamp}},
        upsert=True,
    )

def get_last_gnews_timestamp() -> str | None:
    """Return the last publishedAt timestamp for NewsAPI scraper."""
    record = db.scrape_meta.find_one({"source": "gnews"})
    return record["last_published_at"] if record else None


def update_last_gnews_timestamp(timestamp: str):
    """Update the last fetched timestamp for NewsAPI scraper."""
    db.scrape_meta.update_one(
        {"source": "gnews"},
        {"$set": {"last_published_at": timestamp}},
        upsert=True,
    )

def drop_collections():
    db.reddit_posts.drop()
    print("🗑️ reddit_posts Dropped !")
    db.scrape_meta.drop()
    print("🗑️ scrape_meta Dropped !")
    db.newsapi_articles.drop()
    print("🗑️ newsapi_articles Dropped !")
    db.gnews_articles.drop()
    print("🗑️ gnews_articles Dropped !")
