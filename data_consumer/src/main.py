import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Final

from elasticsearch import Elasticsearch, helpers
from kafka import KafkaConsumer

KAFKA_BROKER: Final[str] = "localhost:9092"
KAFKA_TOPIC: Final[str] = "comments"
ES_HOST: Final[str] = "localhost"
ES_PORT: Final[int] = 9200
ES_INDEX: Final[str] = "comments"


class MessageConsumer(ABC):
    @abstractmethod
    def consume(self):
        pass


class KafkaMessageConsumer(MessageConsumer):
    def __init__(self, broker: str, topic: str, value_deserializer):
        self.broker = broker
        self.topic = topic
        self.value_deserializer = value_deserializer
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=[self.broker],
            auto_offset_reset="earliest",
            value_deserializer=self.value_deserializer,
        )

    def consume(self):
        for message in self.consumer:
            yield message.value


class DocumentIndexer(ABC):
    @abstractmethod
    def index_documents(self, documents: list):
        pass

    @abstractmethod
    def prepare_document(self, data: dict):
        pass


class ElasticsearchDocumentIndexer(DocumentIndexer):
    def __init__(self, es_host: str, es_port: int, es_index: str):
        self.es = Elasticsearch(
            [{"host": es_host, "port": es_port, "scheme": "http"}], verify_certs=False
        )
        self.es_index = es_index
        self.__define_mapping()

    def index_documents(self, documents: list):
        try:
            helpers.bulk(self.es, documents, index=self.es_index)
            print(f"Indexed {len(documents)} documents")
        except Exception as e:
            print(f"Error indexing documents: {e}")

    def prepare_document(self, data: dict) -> dict:
        """Prepare and rename the document fields before indexing."""
        renamed_data = {
            "Name": data["title"],
            "Username": data["author"],
            "Category": data["genre"],
            "Text": data["content"],
            "inserted_at": datetime.now().isoformat(),
        }
        return renamed_data

    def __define_mapping(self):
        """Define the mapping for the index."""
        mapping = {
            "mappings": {
                "properties": {
                    "Name": {"type": "text"},
                    "Username": {"type": "keyword"},
                    "Category": {"type": "keyword"},
                    "Text": {"type": "text"},
                    "inserted_at": {"type": "date"},
                }
            }
        }

        if not self.es.indices.exists(index=self.es_index):
            try:
                self.es.indices.create(index=self.es_index, body=mapping)
                print(f"Index '{self.es_index}' created with mappings.")
            except Exception as e:
                print(f"Error creating index: {e}")
        else:
            print(f"Index '{self.es_index}' already exists.")


class KafkaToElasticsearchService:
    def __init__(
        self, consumer: MessageConsumer, indexer: DocumentIndexer, batch_size: int = 100
    ):
        self.consumer = consumer
        self.indexer = indexer
        self.batch_size = batch_size

    def process_messages(self):
        batch = []
        for message in self.consumer.consume():
            prepared_message = self.indexer.prepare_document(data=message)
            doc = {
                "_op_type": "index",
                "_index": self.indexer.es_index,
                "_source": prepared_message,
            }

            batch.append(doc)

            if len(batch) >= self.batch_size:
                self.indexer.index_documents(batch)
                batch = []

        if batch:
            self.indexer.index_documents(batch)


def main():
    kafka_consumer = KafkaMessageConsumer(
        broker=KAFKA_BROKER,
        topic=KAFKA_TOPIC,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    es_indexer = ElasticsearchDocumentIndexer(
        es_host=ES_HOST,
        es_port=ES_PORT,
        es_index=ES_INDEX,
    )

    service = KafkaToElasticsearchService(
        consumer=kafka_consumer,
        indexer=es_indexer,
    )

    service.process_messages()


if __name__ == "__main__":
    main()
