# Task Management API

A beginner-friendly REST API for managing tasks, built with Python and FastAPI.

This project implements complete CRUD (Create, Read, Update, Delete) operations with input validation, proper HTTP status codes, PostgreSQL persistence, Docker containerization, and interactive Swagger API documentation.

The project was developed progressively through three stages:

- **A1:** In-memory task storage
- **A2:** SQLite database
- **A3:** PostgreSQL with Docker and Docker Compose

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- Psycopg
- Docker
- Docker Compose
- Git & GitHub

## Features

- Create tasks
- View all tasks
- View a single task by ID
- Update tasks
- Delete tasks
- Validate task titles
- Handle 404 errors for missing tasks
- Persistent PostgreSQL storage
- Dockerized FastAPI application
- Dockerized PostgreSQL database
- Docker Compose setup
- PostgreSQL health check
- Interactive Swagger documentation

## Installation & Running Locally

Create and activate a virtual environment:

```bash
python -m venv venv
```

### Git Bash

```bash
source venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a template.

Example:

```text
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

Make sure PostgreSQL is running, then start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Running with Docker Compose

This project uses Docker Compose to run the FastAPI application and PostgreSQL database together.

Make sure Docker Desktop is running.

### Start the application

```bash
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

To stop the application:

```bash
docker compose down
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check that the API is running |
| GET | `/health` | Health check |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{task_id}` | Get a task by ID |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Example API Requests

### Get all tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Get a specific task

```bash
curl http://127.0.0.1:8000/tasks/1
```

### Create a Task

```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Learn Docker\"}"
```

### Update a Task

```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Master Docker\"}"
```

### Delete a Task

```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

## Validation

A task title cannot be empty or missing.

Example:

```json
{
  "title": ""
}
```

Returns:

```text
400 Bad Request
```

## Error Handling

If a task ID does not exist, the API returns:

```json
{
  "detail": "Task not found"
}
```

with:

```text
404 Not Found
```

## Status Codes

| Status Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Task successfully created |
| 204 | Task successfully deleted |
| 400 | Invalid task data |
| 404 | Task not found |

## PostgreSQL Database

The A3 version of this project uses PostgreSQL for persistent task storage.

PostgreSQL runs inside a Docker container when using Docker Compose.

The FastAPI application connects to PostgreSQL using the `DATABASE_URL` environment variable.

The database and `tasks` table are automatically created when the application starts if they do not already exist.

## Database Persistence

PostgreSQL uses a named Docker volume called `taskdata`.

This allows database data to persist when the containers are stopped and started again.

The database can be inspected directly using:

```bash
docker compose exec db psql -U postgres -d tasks
```

Example SQL query:

```sql
SELECT * FROM tasks;
```

This displays all tasks currently stored in PostgreSQL.

## Environment Variables

The project uses a `.env` file for the database connection.

Example:

```text
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

The `.env` file is ignored by Git and should not be committed to the repository.

The `.env.example` file is included as a template.

## Docker Compose Architecture

```text
                    Docker Compose
                         |
             +-----------+-----------+
             |                       |
             v                       v
       FastAPI API             PostgreSQL
       Port 8000                Port 5432
             |                       |
             +-----------+-----------+
                         |
                         v
                  Docker Volume
                     taskdata
```

A PostgreSQL health check ensures that the API starts only after the database is ready.

## Swagger Documentation

The API includes interactive Swagger documentation provided by FastAPI.

Open:

```text
http://127.0.0.1:8000/docs
```

![Swagger Docker Screenshot](Swagger-Docker-Screenshot.png)

## Project Structure

```text
task-management-api/
│
├── main.py
├── database.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── README.md
└── Swagger-Docker-Screenshot.png
```

## Storage Evolution

```text
A1
In-memory list
     |
     v
A2
SQLite
     |
     v
A3
PostgreSQL
     |
     v
Docker + Docker Compose
```

## Docker Files

### Dockerfile

The Dockerfile creates an image containing the FastAPI application and its Python dependencies.

### compose.yaml

Docker Compose starts:

- FastAPI application
- PostgreSQL database
- PostgreSQL persistent volume

The Compose configuration also includes a PostgreSQL health check so the API waits for the database to become ready.

## Status

The application supports complete CRUD operations with PostgreSQL persistence and can be started using Docker Compose.

## Author

Tejashwini