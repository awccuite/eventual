# Eventual

FastAPI application with PostgreSQL and SQLAlchemy.

## Quick Start

Clone the repository:
```bash
git clone <repository-url>
cd eventual
```

Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start PostgreSQL:
```bash
docker-compose up -d
```

Run the application:
```bash
python -m uvicorn app.main:app --reload
```

Access the API:
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/test - Run test suite

## Endpoints

Users:
- POST /users/ - Create user
- GET /users/ - List users
- GET /users/{id} - Get user
- PUT /users/{id} - Update user
- DELETE /users/{id} - Delete user

Tasks:
- POST /tasks/ - Create task
- GET /tasks/ - List tasks
- GET /tasks/{id} - Get task
- PUT /tasks/{id} - Update task
- DELETE /tasks/{id} - Delete task

## Database

Stop database:
```bash
docker-compose down
```

Reset database (deletes all data):
```bash
docker-compose down -v
docker-compose up -d
```
