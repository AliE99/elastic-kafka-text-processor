from typing import Optional

from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI, HTTPException

from src.models.models import SearchParams, TagRequest
from src.services.elasticsearch_service import ElasticsearchService

app = FastAPI()

es = Elasticsearch("http://localhost:9200")

es_service = ElasticsearchService(es)


@app.get("/search/")
async def search_comments(params: SearchParams = Depends()):
    return es_service.search(params)


@app.post("/tag/")
async def tag_document(tag_request: TagRequest):
    es_service.update_document_tag(tag_request.document_id, tag_request.tag)
    return {"message": "Document tagged successfully", "tag": tag_request.tag}
