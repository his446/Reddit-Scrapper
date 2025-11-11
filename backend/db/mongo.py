import asyncio
from datetime import datetime
import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "news")

# Create the client & db at module load
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def connect_db():
    """Initialize MongoDB indexes (id for posts, url for articles)."""
    db.reddit_posts.create_index([("id", ASCENDING)], unique=True, sparse=True)
    db.articles.create_index([("url", ASCENDING)], unique=True, sparse=True)
    db.scrape_meta.create_index([("subreddit", ASCENDING)], unique=True, sparse=True)
    print("✅ Connected to MongoDB!")


def close_db():
    """Close MongoDB client connection."""
    client.close()
    print("🛑 Closed MongoDB connection!")


def save_post(post: dict):
    """save or update a Reddit post."""
    if "created_utc" not in post:
        post["created_utc"] = datetime.now()
    if "saved_utc" not in post:
        post["saved_utc"] = datetime.now()

    db.reddit_posts.update_one({"id": post.get("id")}, {"$set": post}, upsert=True)

def get_last_timestamp(subreddit:str) -> float:
    """"Return the last created_utc timestamp for a subreddit."""
    record = db.scrape_meta.find_one({"subreddit":subreddit})
    return record["last_created_utc"] if record else 0.0

def update_last_timestamp(subreddit:str, timestamp: float):
    """Update the last fetched timestamp for a subreddit."""
    db.scrape_meta.update_one(
        {"subreddit":subreddit},
        {"$set": {"last_created_utc":timestamp}},
        upsert=True
    )
    
def drop_collections():
    db.reddit_posts.drop()
    db.scrape_meta.drop()
    print("🗑️ reddit_posts Dropped !")