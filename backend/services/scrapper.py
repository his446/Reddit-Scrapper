from dotenv import load_dotenv
import os
import praw
from typing import Literal
load_dotenv()
client_id=os.getenv("CLIENT_ID", "")
client_secret=os.getenv("CLIENT_SECRET", "")
user_agent=os.getenv("USER_AGENT", "")

print(client_id)

class RedditScrapper(object):
    def __init__(self):
        self.TARGET_SUBS = ["Futurology", "worldnews", "technology", "MachineLearning", "artificial"]
        self.KEYWORDS = ["AI", "artificial intelligence", "GPT", "OpenAI", "automation", "machine learning"]
        self.client_id=os.getenv("CLIENT_ID", "")
        self.client_secret=os.getenv("CLIENT_SECRET", "")
        self.user_agent=os.getenv("USER_AGENT", "")
    
    def scrape(self, type:Literal["top", "hot", "new", "best", ]):
        pass

class NewsApiScrapper(object):
    def __init__(self):
        pass
    pass   

# subreddits = ["news", "worldnews", "politics", "technolgy", "economics"]

# reddit = praw.Reddit(
#     client_id=client_id,
#     client_secret=client_secret,
#     user_agent=user_agent
# )
# print(reddit.read_only)
# subreddit = reddit.subreddit("news")
# for post in subreddit.new(limit=5):
#     print(post.keys())
