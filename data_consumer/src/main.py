import json
from abc import ABC, abstractmethod
from datetime import datetime

from elasticsearch import Elasticsearch, helpers
from kafka import KafkaConsumer


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
            "Username": data["author"],  # Example username
            "Category": data["genre"],
            "Text": data["content"],
            "inserted_at": datetime.now().isoformat(),  # Current timestamp
        }
        return renamed_data

    def __define_mapping(self):
        """Define the mapping for the index."""
        mapping = {
            "mappings": {
                "properties": {
                    "Name": {"type": "text"},  # For full-text search
                    "Username": {"type": "keyword"},  # For exact match search
                    "Category": {"type": "keyword"},  # For exact match search
                    "Text": {"type": "text"},  # For full-text search
                    "inserted_at": {"type": "date"},  # Timestamp type
                }
            }
        }

        # Check if the index exists, and create it if it doesn't
        if not self.es.indices.exists(index=self.es_index):
            try:
                # Create the index with the specified mapping
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
            # Assuming message is already a dictionary and ready to be indexed
            prepared_message = self.indexer.prepare_document(data=message)
            doc = {
                "_op_type": "index",
                "_index": self.indexer.es_index,
                "_source": prepared_message,
            }

            batch.append(doc)

            # If batch is full, index it
            if len(batch) >= self.batch_size:
                self.indexer.index_documents(batch)
                batch = []  # Clear the batch after indexing

        # Index remaining documents if any
        if batch:
            self.indexer.index_documents(batch)


def main():
    kafka_broker = "localhost:9092"
    kafka_topic = "comments"
    es_host = "localhost"
    es_port = 9200
    es_index = "comments"

    # Create Kafka consumer
    kafka_consumer = KafkaMessageConsumer(
        broker=kafka_broker,
        topic=kafka_topic,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    # Create Elasticsearch indexer
    es_indexer = ElasticsearchDocumentIndexer(
        es_host=es_host, es_port=es_port, es_index=es_index
    )

    # Create service to handle the Kafka-to-Elasticsearch process
    service = KafkaToElasticsearchService(consumer=kafka_consumer, indexer=es_indexer)

    # Start processing messages
    service.process_messages()


if __name__ == "__main__":
    main()
