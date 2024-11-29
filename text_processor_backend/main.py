from fastapi import FastAPI, Query, HTTPException
from elasticsearch import Elasticsearch
from typing import Optional
from datetime import date
from pydantic import BaseModel

app = FastAPI()

es = Elasticsearch("http://localhost:9200")


# Pydantic model for tagging request body
class TagRequest(BaseModel):
    document_id: str
    tag: int  # Single tag (must be 1, 2, or 3)


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


@app.post("/tag/")
async def tag_document(tag_request: TagRequest):
    # Validate that the tag is one of 1, 2, or 3
    valid_tags = {1, 2, 3}
    if tag_request.tag not in valid_tags:
        raise HTTPException(status_code=400, detail="Tag must be one of 1, 2, or 3.")

    # Update the document in Elasticsearch with the tag
    try:
        # Update document's tag in Elasticsearch
        response = es.update(
            index="comments",
            id=tag_request.document_id,
            body={"doc": {"tag": tag_request.tag}},  # Store the single tag
        )

        # Check if the document was found and updated
        if response.get("result") != "updated":
            raise HTTPException(status_code=404, detail="Document not found.")

        return {"message": "Document tagged successfully", "tag": tag_request.tag}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating document: {str(e)}"
        )
