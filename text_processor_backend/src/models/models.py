from fastapi import Query
from typing import Optional
from datetime import date
from pydantic import BaseModel


class TagRequest(BaseModel):
    document_id: str
    tag: int


class SearchParams(BaseModel):
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
