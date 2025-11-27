from pydantic import BaseModel
from typing import List, Optional


class BookSummary(BaseModel):
    book_id: str
    title: str
    snippet: str
    cover_url: Optional[str] = None
    score: float


class BookDetail(BaseModel):
    book_id: str
    title: str
    content: str
    cover_url: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[BookSummary]
