from typing import Optional
from pydantic import BaseModel


class PostIn(BaseModel):
    id: Optional[str]
    source: str
    subreddit: Optional[str]
    author: str
    tittle: str
    body: Optional[str]
    score: int
    url: str
    created_utc: str
    upvote_ratio: float
    comments_num: int


{'id': '1gq4acr', 'title': 'Gemini told my brother to DIE??? Threatening response completely irrelevant to the prompt…', 'author': Redditor(name='dhersie'), 'subreddit': Subreddit(display_name='artificial'), 'score': 1714, 'upvote_ratio': 0.95, 'num_comments': 725, 'created_utc': 1731470436.0, 'url': 'https://i.redd.it/uwfg6tlkel0e1.jpeg',
 'permalink': '/r/artificial/comments/1gq4acr/gemini_told_my_brother_to_die_threatening/', 'selftext': 'Has anyone experienced anything like this? We are thoroughly freaked out. It was acting completely normal prior to this…\n\nHere’s the link the full conversation: https://g.co/gemini/share/6d141b742a13\n'}
