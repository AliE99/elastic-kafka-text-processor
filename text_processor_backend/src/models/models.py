from datetime import date
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class TagRequest(BaseModel):
    document_id: str
    Tag: int


class SearchParams(BaseModel):
    page: Optional[int] = Query(0, description="Starting point")
    size: Optional[int] = Query(100, description="Number of results to return per page")
    name: Optional[str] = Query(None, description="Full-text search on 'Name' field")
    username: Optional[str] = Query(None, description="Exact match on 'Username' field")
    category: Optional[str] = Query(None, description="Exact match on 'Category' field")
    text: Optional[str] = Query(None, description="Full-text search on 'Text' field")
    start_date: Optional[date] = Query(
        None, description="Start date for 'inserted_at' filter (YYYY-MM-DD)"
    )
    end_date: Optional[date] = Query(
        None, description="End date for 'inserted_at' filter (YYYY-MM-DD)"
    )


class Comment(BaseModel):
    id: str
    Name: str
    Username: str
    Category: str
    Text: str
    Tag: Optional[int] = None
