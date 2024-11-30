from typing import Optional

from elasticsearch import Elasticsearch
from fastapi import HTTPException

from src.main import SearchParams
from src.models.models import Comment, SearchParams


class ElasticsearchService:
    def __init__(self, es_client: Elasticsearch):
        self.es = es_client

    def search(self, params: Optional[SearchParams]) -> list[Comment]:
        query_body = self.__create_es_query(params=params)
        response = self.es.search(index="comments", body=query_body)
        return [
            Comment(id=hit["_id"], **hit["_source"]) for hit in response["hits"]["hits"]
        ]

    def validate_tag(self, tag: int) -> bool:
        valid_tags = {1, 2, 3}
        return tag in valid_tags

    def update_document_tag(self, document_id: str, tag: int) -> dict:
        if not self.validate_tag(tag):
            raise HTTPException(
                status_code=400, detail="Tag must be one of 1, 2, or 3."
            )

        try:
            response = self.es.update(
                index="comments",
                id=document_id,
                body={"doc": {"Tag": tag}},
            )
            if response.get("result") != "updated":
                raise HTTPException(status_code=404, detail="Document not found.")
            return response
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error updating document: {str(e)}"
            )

    def __create_es_query(self, params: SearchParams) -> dict:
        must_queries = []
        filter_queries = []

        if params.name:
            must_queries.append({"match": {"Name": params.name}})
        if params.text:
            must_queries.append({"match": {"Text": params.text}})
        
        if params.username:
            filter_queries.append({"term": {"Username": params.username}})
        if params.category:
            filter_queries.append({"term": {"Category": params.category}})

        if params.id:
            filter_queries.append({"terms": {"_id": [params.id]}})

        if params.start_date or params.end_date:
            date_filter = {"range": {"inserted_at": {}}}
            if params.start_date:
                date_filter["range"]["inserted_at"][
                    "gte"
                ] = params.start_date.isoformat()
            if params.end_date:
                date_filter["range"]["inserted_at"]["lte"] = params.end_date.isoformat()
            filter_queries.append(date_filter)

        query_body = {
            "from": params.page,
            "size": params.size,
            "query": {
                "bool": {
                    "must": must_queries,
                    "filter": filter_queries,
                }
            },
        }
        return query_body
