from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class GnewsArticleModel(BaseModel):
    """Schema for Gnews articles stored in MongoDB."""
    url: HttpUrl
    title: str
    author: Optional[str]
    description: Optional[str]
    content: Optional[str]
    expanded_content: Optional[str]
    publishedAt: datetime
    source_id: Optional[str]
    source_name: Optional[str]
    saved_utc: datetime = Field(default_factory=datetime.now)

