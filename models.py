from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Image(BaseModel):
    """Model for news item images."""
    url: HttpUrl
    alt: str

class NestedReaction(BaseModel):
    """Model for nested reactions (replies)."""
    text: str
    language: str = "Unknown"

class Reaction(BaseModel):
    """Model for reactions to news items."""
    user: str = "Unknown"
    text: str
    language: str = "Unknown"
    likes: str = "0"
    nested_reactions: List[NestedReaction] = []

class NewsItem(BaseModel):
    """Model for news items."""
    title: str
    category: str
    reactions_info: str
    reactions_link: Optional[HttpUrl] = None
    reactions: List[Reaction] = []
    article_link: HttpUrl
    image: Optional[Image] = None 