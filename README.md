# Comment Processing Pipeline

## Project Overview
The **Comment Processing Pipeline** is a distributed system consisting of three Dockerized services that handle the processing, indexing, and querying of user-generated comments.

### Services

1. **`api_data_producer`**: 
   - This service makes API calls to retrieve comments written by users and sends them to Kafka for further processing.

2. **`data_consumer`**: 
   - This service reads the data from Kafka and indexes it into Elasticsearch, making it searchable and available for further analysis.

3. **`text_processor_backend`**: 
   - Built with FastAPI, this service provides an API for users to search, filter, and tag comments, enabling interactive and efficient data exploration.
