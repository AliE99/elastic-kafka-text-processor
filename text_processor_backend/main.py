from fastapi import FastAPI, Query
from elasticsearch import Elasticsearch
from typing import Optional
from datetime import date

app = FastAPI()

es = Elasticsearch("http://localhost:9200")


@app.get("/search/")
async def search_comments(
    name: Optional[str] = Query(None, description="Full-text search on 'Name' field"),
    username: Optional[str] = Query(
        None, description="Exact match on 'Username' field"
    ),
    category: Optional[str] = Query(
        None, description="Exact match on 'Category' field"
    ),
    text: Optional[str] = Query(None, description="Full-text search on 'Text' field"),
    start_date: Optional[date] = Query(
        None, description="Start date for 'inserted_at' filter (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for 'inserted_at' filter (YYYY-MM-DD)"
    ),
):
    must_queries = []
    filter_queries = []

    if name:
        must_queries.append({"match": {"Name": name}})
    if text:
        must_queries.append({"match": {"Text": text}})

    if username:
        filter_queries.append({"term": {"Username": username}})
    if category:
        filter_queries.append({"term": {"Category": category}})

    # Date range filter
    if start_date or end_date:
        date_filter = {"range": {"inserted_at": {}}}
        if start_date:
            date_filter["range"]["inserted_at"]["gte"] = start_date.isoformat()
        if end_date:
            date_filter["range"]["inserted_at"]["lte"] = end_date.isoformat()
        filter_queries.append(date_filter)

    query_body = {"query": {"bool": {"must": must_queries, "filter": filter_queries}}}

    response = es.search(index="comments", body=query_body)
    return {"hits": response["hits"]["hits"]}
