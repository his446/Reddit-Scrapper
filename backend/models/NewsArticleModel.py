from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, HttpUrl, field_validator


class NewsArticleModel(BaseModel):
    """Schema for Reddit posts stored in MongoDB."""
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

