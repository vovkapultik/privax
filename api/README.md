# Privax ZK Note Generator API

A FastAPI-based service for generating privacy notes with cryptographic commitments and nullifier hashes. This API allows users to create privacy-preserving notes with unique cryptographic properties.

## Features

- Generate notes with specified amounts
- Cryptographic commitments for privacy
- Nullifier hashes to prevent double-spending
- Customizable secrets
- REST API with OpenAPI documentation

## Project Structure

```
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── routes.py           # API route definitions
│   ├── models.py           # Pydantic models for request/response validation
│   └── crypto/             # Cryptographic functionality
│       ├── __init__.py
│       └── note.py         # Note class implementation
├── tests/                  # Test directory
│   ├── __init__.py
│   ├── test_note.py        # Tests for Note class
│   └── test_api.py         # Tests for API endpoints
├── main.py                 # Legacy entry point (for compatibility)
├── run.py                  # Script to run the API server
├── run_tests.py            # Script to run tests
├── requirements.txt        # Project dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # Project documentation
```

## Setup and Installation

### Local Development

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the API:
   ```
   python run.py
   ```
   Or with uvicorn directly:
   ```
   uvicorn app.main:app --reload
   ```

### Using Docker

1. Build and run with Docker Compose:
   ```
   docker-compose up --build
   ```

## API Usage

Once the server is running, you can access:

- API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/api/v1/health`

### Creating a Note

Send a POST request to `/api/v1/notes` with the following JSON body:

```json
{
  "amount": 100
}
```

Optional parameters:
- `secret`: Custom secret value
- `nullifier_secret`: Custom nullifier secret value

Example response:

```json
{
  "amount": 100,
  "secret": "2a3f1e5d8c7b9a0f6e4d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1",
  "nullifier_secret": "7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a12a3f1e5d8c7b9a0f6e4d2c1b0a9f8e",
  "commitment": "5e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
  "nullifier_hash": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a"
}
```

## Running Tests

```
python run_tests.py
```

Or with pytest:

```
pytest
```

## Notes on the Implementation

This implementation uses SHA256 as a placeholder for a ZK-friendly hash function like Poseidon. In a real ZK application, you would need to replace this with a proper ZK-friendly hash that's compatible with your proving system. 