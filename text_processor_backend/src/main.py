from typing import List

from elasticsearch import Elasticsearch
from fastapi import Depends, FastAPI

from src.models.models import Comment, SearchParams, TagRequest
from src.services.elasticsearch_service import ElasticsearchService

app = FastAPI()

es = Elasticsearch("http://localhost:9200")  # TODO: Add environment variable

es_service = ElasticsearchService(es)


@app.get("/search/", response_model=List[Comment])
async def search_comments(params: SearchParams = Depends()):
    return es_service.search(params)


@app.post("/tag/")
async def tag_comment(tag_request: TagRequest):
    es_service.update_comment_tag(tag_request.id, tag_request.Tag)
    return {"message": "Comment tagged successfully", "tag": tag_request.Tag}
