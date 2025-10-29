from dotenv import load_dotenv
import os
import praw
from typing import Literal
load_dotenv()
# client_id=os.getenv("CLIENT_ID", "")
# client_secret=os.getenv("CLIENT_SECRET", "")
# user_agent=os.getenv("USER_AGENT", "")


class Scrapper(object):
    def __init__(self):
        self.TARGET_SUBS = ["Futurology", "worldnews",
                            "technology", "MachineLearning", "artificial"]
        self.KEYWORDS = os.getenv(
            "KEYWORDS", 'ai+artificial intelligence+gpt+openai+automation+machine learning+deep learning').split("+")

    def text_contains_ai(self, text: str) -> bool:
        if not text:
            return False
        t = text.lower()
        return any(kw in t for kw in self.KEYWORDS)


class RedditScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.client_id = os.getenv("CLIENT_ID", "")
        self.client_secret = os.getenv("CLIENT_SECRET", "")
        self.user_agent = os.getenv("USER_AGENT", "")
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
        return self.text_mentions_ai(post.title or "") or self.text_mentions_ai(getattr(post, "selftext", "") or "")

    def scrape(self, type: Literal["top", "hot", "new", "rising"] = "top", limit: int = 25):
        for sub in self.TARGET_SUBS:
            subreddit = self.praw.subreddit(sub)
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

            for post in posts:
                if self.post_mentions_ai(post):


class NewsApiScrapper(object):
    def __init__(self):
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
rs = RedditScrapper()
rs.scrape()
