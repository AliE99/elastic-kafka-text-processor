# Comment Processing Pipeline

The **Comment Processing Pipeline** is a distributed system consisting of three Dockerized services that handle the processing, indexing, and querying of user-generated comments.

## Table of Contents
- [Project Overview](#project-overview)
- [Installation](#installation)
- [Usage](#usage)

## Project Overview
### Services

1. **`api_data_producer`**: 
   - This service makes API calls to retrieve comments written by users and sends them to Kafka for further processing.

2. **`data_consumer`**: 
   - This service reads the data from Kafka and indexes it into Elasticsearch, making it searchable and available for further analysis.

3. **`text_processor_backend`**: 
   - Built with FastAPI, this service provides an API for users to search, filter, and tag comments, enabling interactive and efficient data exploration.

### Technologies Used
- **Docker**: Containerizes the services for easy deployment.
- **Kafka**: Message queue for decoupling services.
- **Elasticsearch**: Full-text search and indexing.
- **FastAPI**: API framework for building the text processing backend.

## Installation

### Prerequisites
Make sure you have the following installed on your local machine:
- Docker
- Docker Compose

### Steps to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/AliE99/elastic-kafka-text-processor.git
   cd elastic-kafka-text-processor
   ```

2. Build and start the services:
   ```bash
   docker-compose up --build
   ```

## Usage

Once the services are running, you can interact with the **`text_processor_backend`** API to search, filter, and tag comments.

### Search Comments
- **Endpoint**: `GET http://127.0.0.1:8000/search/`
- **Parameters**:
  - `page` (optional): Starting page if results, default is 0.
  - `size` (optional): Number of results to return per page, default is 100.
  - `id` (optional): The comment ID.
  - `name` (optional): The name of the commenter.
  - `username` (optional): The username of the commenter.
  - `category` (optional): The category of the comment.
  - `text` (optional): The content of the comment.
  - `start_date` (optional): The starting date for filtering comments (format: `YYYY-MM-DD`).
  - `end_date` (optional): The ending date for filtering comments (format: `YYYY-MM-DD`).
  - `tag` (optional): The comment Tag.

**Example Request**:
```bash
GET http://127.0.0.1:8000/search/?name=John&start_date=2023-01-01&end_date=2023-12-31
```
**Response Example**:
```json
{
   "id": "EccXd5MBxe2acnTqvErZ",
   "Name": "John Doe",
   "Username": "johnny",
   "Category": "Reiciendis",
   "Text": "This is a great comment!",
   "inserted_at": "2024-11-29T08:44:24.642866",
   "Tag": 1,
}
```
### Tag a Comment
- **Endpoint**: POST `http://127.0.0.1:8000/tags`
- **Parameters**:
  - `id` (required): The unique identifier for the comment.
  - `tag` (required): The tag to be added to the comment.

**Example Request**:
```bash
POST http://127.0.0.1:8000/tags
Content-Type: application/json
{
  "id": EccXd5MBxe2acnTqvErZ,
  "tag": "important"
}
```
**Response Example**:
```json
{
  "message": "Comment tagged successfully",
  "tag": 2
}
```