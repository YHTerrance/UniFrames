# Frame Gen Backend

A FastAPI backend for the Frame Gen application.

## Features

- RESTful API with FastAPI
- Modular project structure
- Sample frame endpoints

## Project Structure

```
/backend
├── app/
│   ├── models/       # Database models
│   ├── routers/      # API routes
│   ├── services/     # Business logic
│   ├── config.py     # Application configuration
│   └── dependencies.py # Dependency injection
├── main.py          # Application entry point
└── requirements.txt  # Project dependencies
```

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc

## Available Endpoints

- `GET /api/v1/frames`: Get all frames
- `GET /api/v1/frames/{frame_id}`: Get a specific frame
- `POST /api/v1/frames`: Create a new frame
- `PUT /api/v1/frames/{frame_id}`: Update a frame
- `DELETE /api/v1/frames/{frame_id}`: Delete a frame