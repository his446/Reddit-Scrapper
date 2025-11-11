from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, field_validator


class RedditPost(BaseModel):
    """Schema for Reddit posts stored in MongoDB."""
    id: str
    title: str
    author: Optional[str] = None
    subreddit: Optional[str] = None
    score: Optional[int] = 0
    upvote_ratio: Optional[float] = None
    num_comments: Optional[int] = 0
    created_utc: Union[datetime, float, int]
    url: Optional[HttpUrl] = None
    permalink: Optional[str] = None
    selftext: Optional[str] = None
    saved_utc: datetime = datetime.now()
    
    @field_validator("created_utc", mode="before")
    def convert_timestamp(cls, v):
        """Convert numeric timestamps to datetime objects."""
        if isinstance(v, (float, int)):
            return datetime.fromtimestamp(v)
        return v
