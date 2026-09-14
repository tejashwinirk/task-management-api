# Task Management API

A beginner-friendly REST API for managing tasks, built with Python and FastAPI.

This project was developed progressively through four backend stages, evolving from simple in-memory CRUD operations to a PostgreSQL-backed, Dockerized API with Supabase authentication, JWT verification, protected routes, and Swagger Bearer authentication.

## Project Progression

- **A1:** In-memory task storage and CRUD API
- **A2:** SQLite database persistence
- **A3:** PostgreSQL with Docker and Docker Compose
- **A4:** Supabase authentication, JWT verification, protected routes, and Swagger Bearer authentication

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- Psycopg
- Supabase Auth
- Supabase Python SDK
- python-dotenv
- Docker
- Docker Compose
- Git & GitHub

## Features

### Task Management

- Create tasks
- View all tasks
- View a single task by ID
- Update tasks
- Delete tasks
- Validate task titles
- Handle missing task IDs
- Persistent PostgreSQL storage

### Authentication & Authorization

- User signup with Supabase Auth
- User login with email and password
- JWT access token authentication
- JWT verification through Supabase
- Protected profile endpoint
- Protected dashboard endpoint
- Protected logout endpoint
- Reusable authentication dependency
- Public endpoint
- Swagger Bearer authentication

### Infrastructure

- Dockerized FastAPI application
- Dockerized PostgreSQL database
- Docker Compose
- PostgreSQL health check
- Persistent Docker volume
- Environment variable configuration

## Installation & Running Locally

Create a virtual environment:

```bash
python -m venv venv

Activate the virtual environment in Git Bash:
source venv/Scripts/activate

Install dependencies:
pip install -r requirements.txt

Create a .env file using .env.example as a template.

The .env file should contain:
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_or_publishable_key

Replace the Supabase placeholders with the values from your Supabase project.

Never commit the real .env file to GitHub.

Make sure PostgreSQL is running, then start the FastAPI server:
uvicorn main:app --reload

The API will be available at:
http://127.0.0.1:8000

Swagger UI:
http://127.0.0.1:8000/docs

Running with Docker Compose

This project uses Docker Compose to run the FastAPI application and PostgreSQL database together.

Make sure Docker Desktop is running.

Start the application:
docker compose up --build

The API will be available at:
http://127.0.0.1:8000

Swagger UI:
http://127.0.0.1:8000/docs

To stop the application:

docker compose down

## API Endpoints

### General Endpoints

METHOD   ENDPOINT       DESCRIPTION
GET      /              Check that the API is running
GET      /health        Health check


### Authentication Endpoints

METHOD   ENDPOINT          AUTHENTICATION   DESCRIPTION
POST     /auth/signup      Public           Create a new user account
POST     /auth/login       Public           Login and receive access and refresh tokens
POST     /auth/logout      Bearer JWT       Logout from the authenticated session


### Public and Protected Endpoints

METHOD   ENDPOINT                  AUTHENTICATION   DESCRIPTION
GET      /public/info              Public           Public information endpoint
GET      /protected/profile        Bearer JWT       Return authenticated user's profile
GET      /protected/dashboard      Bearer JWT       Access the protected dashboard


### Task Endpoints

METHOD   ENDPOINT             DESCRIPTION
GET      /tasks               Get all tasks
GET      /tasks/{task_id}     Get a task by ID
POST     /tasks               Create a new task
PUT      /tasks/{task_id}     Update an existing task
DELETE   /tasks/{task_id}     Delete a task

Authentication is handled using Supabase Auth.

The backend does not store passwords or implement its own password hashing.
Client
   |
   | Signup / Login
   v
Supabase Auth
   |
   | Access Token (JWT)
   v
Client
   |
   | Bearer Token
   v
FastAPI Backend
   |
   | Verify JWT
   v
Supabase Auth
   |
   | Valid User
   v
Protected Endpoint

The backend trusts a request only after the supplied access token has been successfully verified.

Signup

Create a new account using:

POST /auth/signup

Example request:

{
  "email": "test@example.com",
  "password": "your-password"
}

Successful signup returns:

201 Created

The user account is created and managed by Supabase Auth.

Login

Login using:

POST /auth/login

Example request:

{
  "email": "test@example.com",
  "password": "your-password"
}

A successful login returns:

200 OK

with an access token and refresh token.

Example response structure:

{
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token"
}

The access token is used to access protected endpoints.

Protected Routes

Protected routes require a valid Supabase access token.

The token must be sent using the HTTP Bearer authentication scheme:

Authorization: Bearer YOUR_ACCESS_TOKEN

The project uses a reusable FastAPI dependency:

get_current_user

This dependency:

Checks that a Bearer token is present.
Extracts the access token.
Sends the access token to Supabase for verification.
Rejects invalid or expired tokens.
Returns the authenticated user when verification succeeds.

The same dependency is reused by multiple protected routes.

Protected Profile

Endpoint:

GET /protected/profile

Authentication:

Bearer JWT required

A valid token returns safe user information such as:

{
  "id": "user-id",
  "email": "user@example.com"
}
Protected Dashboard

Endpoint:

GET /protected/dashboard

Authentication:

Bearer JWT required

A valid token allows access to the protected dashboard.

Example response structure:

{
  "message": "Welcome to the protected dashboard",
  "user_id": "user-id",
  "email": "user@example.com"
}
Logout

Endpoint:

POST /auth/logout

Authentication:

Bearer JWT required

A successful request returns:

204 No Content
Public Endpoint

The project also includes a public endpoint:

GET /public/info

This endpoint does not require authentication.

Example response:

{
  "message": "This is a public endpoint"
}
Authentication Error Handling

Protected routes reject requests when authentication is missing or invalid.

Missing token
401 Unauthorized
Invalid or expired token
401 Unauthorized

The backend verifies the JWT using Supabase rather than trusting the token contents directly.

Task API Examples
Get all tasks
curl http://127.0.0.1:8000/tasks
Get a specific task
curl http://127.0.0.1:8000/tasks/1
Create a task
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Learn Docker\"}"
Update a task
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Master Docker\"}"
Delete a task
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
Validation

A task title cannot be empty or missing.

Example:

{
  "title": ""
}

Returns:

400 Bad Request
Error Handling

If a task ID does not exist, the API returns:

{
  "detail": "Task not found"
}

with:

404 Not Found

Authentication failures return:

401 Unauthorized

## Status Codes

STATUS CODE   MEANING
200           Successful request
201           Resource successfully created
204           Successful request with no response body
400           Invalid request data
401           Authentication required or invalid
404           Resource not found

Yes — I understand now. You want one single complete README, not pieces or sections that you have to combine yourself.

Copy everything inside this ONE code block and replace your entire README.md with it:

# Task Management API

A beginner-friendly REST API for managing tasks, built with Python and FastAPI.

This project was developed progressively through four backend stages, evolving from simple in-memory CRUD operations to a PostgreSQL-backed, Dockerized API with Supabase authentication, JWT verification, protected routes, and Swagger Bearer authentication.

## Project Progression

- **A1:** In-memory task storage and CRUD API
- **A2:** SQLite database persistence
- **A3:** PostgreSQL with Docker and Docker Compose
- **A4:** Supabase authentication, JWT verification, protected routes, and Swagger Bearer authentication

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL
- Psycopg
- Supabase Auth
- Supabase Python SDK
- python-dotenv
- Docker
- Docker Compose
- Git & GitHub

## Features

### Task Management

- Create tasks
- View all tasks
- View a single task by ID
- Update tasks
- Delete tasks
- Validate task titles
- Handle missing task IDs
- Persistent PostgreSQL storage

### Authentication & Authorization

- User signup with Supabase Auth
- User login with email and password
- JWT access token authentication
- JWT verification through Supabase
- Protected profile endpoint
- Protected dashboard endpoint
- Protected logout endpoint
- Reusable authentication dependency
- Public endpoint
- Swagger Bearer authentication

### Infrastructure

- Dockerized FastAPI application
- Dockerized PostgreSQL database
- Docker Compose
- PostgreSQL health check
- Persistent Docker volume
- Environment variable configuration

## Installation & Running Locally

Create a virtual environment:

```bash
python -m venv venv

Activate the virtual environment in Git Bash:

source venv/Scripts/activate

Install dependencies:

pip install -r requirements.txt

Create a .env file using .env.example as a template.

The .env file should contain:

DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_or_publishable_key

Replace the Supabase placeholders with the values from your Supabase project.

Never commit the real .env file to GitHub.

Make sure PostgreSQL is running, then start the FastAPI server:

uvicorn main:app --reload

The API will be available at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs
Running with Docker Compose

This project uses Docker Compose to run the FastAPI application and PostgreSQL database together.

Make sure Docker Desktop is running.

Start the application:

docker compose up --build

The API will be available at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

To stop the application:

docker compose down
API Endpoints
General Endpoints
Method	Endpoint	Description
GET	/	Check that the API is running
GET	/health	Health check
Authentication Endpoints
Method	Endpoint	Authentication	Description
POST	/auth/signup	Public	Create a new user account
POST	/auth/login	Public	Login and receive access and refresh tokens
POST	/auth/logout	Bearer JWT	Logout from the authenticated session
Public and Protected Endpoints
Method	Endpoint	Authentication	Description
GET	/public/info	Public	Public information endpoint
GET	/protected/profile	Bearer JWT	Return authenticated user's profile
GET	/protected/dashboard	Bearer JWT	Access the protected dashboard
Task Endpoints
Method	Endpoint	Description
GET	/tasks	Get all tasks
GET	/tasks/{task_id}	Get a task by ID
POST	/tasks	Create a new task
PUT	/tasks/{task_id}	Update an existing task
DELETE	/tasks/{task_id}	Delete a task
Authentication Flow

Authentication is handled using Supabase Auth.

The backend does not store passwords or implement its own password hashing.

Client
   |
   | Signup / Login
   v
Supabase Auth
   |
   | Access Token (JWT)
   v
Client
   |
   | Bearer Token
   v
FastAPI Backend
   |
   | Verify JWT
   v
Supabase Auth
   |
   | Valid User
   v
Protected Endpoint

The backend trusts a request only after the supplied access token has been successfully verified.

Signup

Create a new account using:

POST /auth/signup

Example request:

{
  "email": "test@example.com",
  "password": "your-password"
}

Successful signup returns:

201 Created

The user account is created and managed by Supabase Auth.

Login

Login using:

POST /auth/login

Example request:

{
  "email": "test@example.com",
  "password": "your-password"
}

A successful login returns:

200 OK

with an access token and refresh token.

Example response structure:

{
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token"
}

The access token is used to access protected endpoints.

Protected Routes

Protected routes require a valid Supabase access token.

The token must be sent using the HTTP Bearer authentication scheme:

Authorization: Bearer YOUR_ACCESS_TOKEN

The project uses a reusable FastAPI dependency:

get_current_user

This dependency:

Checks that a Bearer token is present.
Extracts the access token.
Sends the access token to Supabase for verification.
Rejects invalid or expired tokens.
Returns the authenticated user when verification succeeds.

The same dependency is reused by multiple protected routes.

Protected Profile

Endpoint:

GET /protected/profile

Authentication:

Bearer JWT required

A valid token returns safe user information such as:

{
  "id": "user-id",
  "email": "user@example.com"
}
Protected Dashboard

Endpoint:

GET /protected/dashboard

Authentication:

Bearer JWT required

A valid token allows access to the protected dashboard.

Example response structure:

{
  "message": "Welcome to the protected dashboard",
  "user_id": "user-id",
  "email": "user@example.com"
}
Logout

Endpoint:

POST /auth/logout

Authentication:

Bearer JWT required

A successful request returns:

204 No Content
Public Endpoint

The project also includes a public endpoint:

GET /public/info

This endpoint does not require authentication.

Example response:

{
  "message": "This is a public endpoint"
}
Authentication Error Handling

Protected routes reject requests when authentication is missing or invalid.

Missing token
401 Unauthorized
Invalid or expired token
401 Unauthorized

The backend verifies the JWT using Supabase rather than trusting the token contents directly.

Task API Examples
Get all tasks
curl http://127.0.0.1:8000/tasks
Get a specific task
curl http://127.0.0.1:8000/tasks/1
Create a task
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Learn Docker\"}"
Update a task
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Master Docker\"}"
Delete a task
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
Validation

A task title cannot be empty or missing.

Example:

{
  "title": ""
}

Returns:

400 Bad Request
Error Handling

If a task ID does not exist, the API returns:

{
  "detail": "Task not found"
}

with:

404 Not Found

Authentication failures return:

401 Unauthorized
Status Codes
Status Code	Meaning
200	Successful request
201	Resource successfully created
204	Successful request with no response body
400	Invalid request data
401	Authentication required or invalid
404	Resource not found
PostgreSQL Database

The A3 and A4 versions of this project use PostgreSQL for persistent task storage.

PostgreSQL can run inside Docker when using Docker Compose.

The FastAPI application connects to PostgreSQL using the DATABASE_URL environment variable.

The database and tasks table are automatically created when the application starts if they do not already exist.

Database Persistence

PostgreSQL uses a named Docker volume called:

taskdata

This allows database data to persist when containers are stopped and started again.

The database can be inspected directly using:

docker compose exec db psql -U postgres -d tasks

Example SQL query:

SELECT * FROM tasks;
Environment Variables

The project uses environment variables for configuration.

The local .env file contains:

DATABASE_URL=...
SUPABASE_URL=...
SUPABASE_KEY=...

The .env file is ignored by Git and must not be committed to the repository.

A safe .env.example file is included with placeholder values:

DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_or_publishable_key

This allows other developers to understand which environment variables are required without exposing credentials.

Docker Compose Architecture
                 Docker Compose
                       |
          +------------+------------+
          |                         |
          v                         v
     FastAPI API              PostgreSQL
     Port 8000                Port 5432
          |                         |
          +------------+------------+
                       |
                       v
                 Docker Volume
                    taskdata

A PostgreSQL health check ensures that the API starts only after the database is ready.

Swagger Documentation

The API includes interactive Swagger documentation provided by FastAPI.

Open:

http://127.0.0.1:8000/docs

Swagger supports Bearer authentication for the protected endpoints.

The Authorize button can be used to provide a valid Supabase access token.

Enter:

Bearer YOUR_ACCESS_TOKEN

After authorization, protected endpoints can be tested directly from Swagger.

Project Structure
task-management-api/

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
Storage Evolution
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
     |
     v
A4
Supabase Authentication + JWT Protection
Docker Files
Dockerfile

The Dockerfile creates an image containing the FastAPI application and its Python dependencies.

compose.yaml

Docker Compose starts:

FastAPI application
PostgreSQL database
PostgreSQL persistent volume

The Compose configuration also includes a PostgreSQL health check so the API waits for the database to become ready.

Security Notes
Passwords are handled by Supabase Auth.
Password hashing is not implemented manually in the backend.
Supabase access tokens are verified before protected resources are returned.
The .env file is excluded from Git.
.env.example contains placeholders only.
Supabase credentials should never be committed to the repository.
Protected endpoints require a valid Bearer token.
Status

The application supports:

Complete task CRUD operations
PostgreSQL persistence
Docker and Docker Compose
Supabase user authentication
JWT verification
Protected API routes
Reusable authentication dependency
Swagger Bearer authentication

The project can be started locally or using Docker Compose.

Author

Tejashwini