from dotenv import load_dotenv
import os
import praw

load_dotenv()
client_id=os.getenv("CLIENT_ID", "")
client_secret=os.getenv("CLIENT_SECRET", "")
user_agent=os.getenv("USER_AGENT", "")

subreddits = ["news", "worldnews", "politics", "technolgy", "economics"]

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)
print(reddit.read_only)
# subreddit = reddit.subreddit("news")
# for post in subreddit.hot(limit=5):
#     print(post.title)

