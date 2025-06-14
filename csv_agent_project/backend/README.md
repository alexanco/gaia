# NF-e Question Answering API

This is a FastAPI-based REST API that provides question answering capabilities for Brazilian electronic invoices (NF-e) using LangChain and Deepseek.

## Prerequisites

- Docker and Docker Compose
- Deepseek API key

## Setup

1. Clone the repository
2. Copy the example environment file:
   ```bash
   cp env.example .env
   ```
3. Edit `.env` and add your Deepseek API key
4. Place your CSV files in the `data` directory:
   - `202401_NFs_Cabecalho.csv`
   - `202401_NFs_Itens.csv`

## Running the API

Start the API using Docker Compose:

```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

## API Endpoints

### Health Check
- GET `/health`
  - Returns the API health status

### Ask Question
- POST `/question`
  - Request body:
    ```json
    {
        "question": "What is the total value of all invoices?"
    }
    ```
  - Response:
    ```json
    {
        "answer": "The answer to your question..."
    }
    ```

## API Documentation

Once the API is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
