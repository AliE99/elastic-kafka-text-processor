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
        return (
            EsQueryBuilder(params)
            .add_id()
            .add_name()
            .add_text()
            .add_username()
            .add_category()
            .add_date_range()
            .build()
        )


class EsQueryBuilder:
    def __init__(self, params: SearchParams):
        self.params = params
        self.must_queries = []
        self.filter_queries = []

    def add_id(self):
        if self.params.id:
            self.filter_queries.append({"terms": {"_id": [self.params.id]}})
        return self

    def add_name(self):
        if self.params.name:
            self.must_queries.append({"match": {"Name": self.params.name}})
        return self

    def add_text(self):
        if self.params.text:
            self.must_queries.append({"match": {"Text": self.params.text}})
        return self

    def add_username(self):
        if self.params.username:
            self.filter_queries.append({"term": {"Username": self.params.username}})
        return self

    def add_category(self):
        if self.params.category:
            self.filter_queries.append({"term": {"Category": self.params.category}})
        return self

    def add_date_range(self):
        if self.params.start_date or self.params.end_date:
            date_filter = {"range": {"inserted_at": {}}}
            if self.params.start_date:
                date_filter["range"]["inserted_at"][
                    "gte"
                ] = self.params.start_date.isoformat()
            if self.params.end_date:
                date_filter["range"]["inserted_at"][
                    "lte"
                ] = self.params.end_date.isoformat()
            self.filter_queries.append(date_filter)
        return self

    def build(self) -> dict:
        return {
            "from": self.params.page,
            "size": self.params.size,
            "query": {
                "bool": {
                    "must": self.must_queries,
                    "filter": self.filter_queries,
                }
            },
        }
