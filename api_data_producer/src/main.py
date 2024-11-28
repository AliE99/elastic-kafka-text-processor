import json
import time

import requests
import schedule
from kafka import KafkaProducer


class APIClient:
    """Handles API requests and response processing."""

    def __init__(self, url: str):
        self.url: str = url

    def fetch_data(self):
        """Fetch data from the API endpoint."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()["data"]  # Return only the 'data' part
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None


class KafkaService:
    """Handles communication with Kafka."""

    def __init__(self, kafka_server: str, topic: str):
        self.kafka_server: str = kafka_server
        self.topic: str = topic
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_server,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode(
                "utf-8"
            ),  # For Persian characters
        )

    def send_to_kafka(self, message):
        """Send a single message to Kafka."""
        try:
            self.producer.send(self.topic, message)
            print(f"Message sent to Kafka: {message}")
        except Exception as e:
            print(f"Error sending message to Kafka: {e}")


class Application:
    """Main application for fetching, processing, and saving data to Kafka."""

    def __init__(self, api_client, kafka_service):
        self.api_client: APIClient = api_client
        self.kafka_service: KafkaService = kafka_service

    def run(self):
        """Run the application workflow."""
        print("Fetching data from API...")
        data = self.api_client.fetch_data()

        if data:
            print("Sending data to Kafka...")
            for record in data:
                self.kafka_service.send_to_kafka(record)

            print("All data sent to Kafka successfully.")
        else:
            print("No data to process.")


# Constants
API_URL = "https://fakerapi.it/api/v2/texts?_quantity=100&_locale=fa_IR"
KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "comments"

# Initialize components
api_client = APIClient(API_URL)
kafka_service = KafkaService(KAFKA_SERVER, KAFKA_TOPIC)

# Run the application
app = Application(api_client, kafka_service)

schedule.every(60).seconds.do(app.run)
while True:
    schedule.run_pending()
    time.sleep(1)
