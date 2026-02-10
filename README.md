# FastAPI REST App

A RESTful API built with FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `POST /items` - Create a new item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

## Project Structure

```
ProjectFastAPI/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore file
└── README.md           # This file
```
