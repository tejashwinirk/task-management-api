from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from database import initialize_database, get_connection, supabase


app = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

security = HTTPBearer(auto_error=False)


# -----------------------------
# Custom Error Handler
# -----------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"error": exc.detail}
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# -----------------------------
# Models
# -----------------------------

class TaskCreate(BaseModel):
    title: str | None = None


class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None


# -----------------------------
# Authentication Dependency
# -----------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        return response.user

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# -----------------------------
# General Routes
# -----------------------------

@app.get("/")
def root():
    return {
        "message": "Task Management API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# Authentication Routes
# -----------------------------

@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):
    if not data.email or not data.email.strip():
        raise HTTPException(
            status_code=400,
            detail="Email is required"
        )

    if not data.password or not data.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Password is required"
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": data.email,
                "password": data.password
            }
        )

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Signup failed"
            )

        return {
            "id": response.user.id,
            "email": response.user.email
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Signup failed"
        )


@app.post("/auth/login")
def login(data: AuthRequest):
    if not data.email or not data.email.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Email is required"}
        )

    if not data.password or not data.password.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Password is required"}
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": data.email,
                "password": data.password
            }
        )

        if response.session is None:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid login credentials"}
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )


@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):
    return


# -----------------------------
# Public Routes
# -----------------------------

@app.get("/public/info")
def public_info():
    return {
        "message": "This is a public endpoint"
    }


# -----------------------------
# Protected Routes
# -----------------------------

@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }


@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):
    return {
        "message": "Welcome to the protected dashboard",
        "user_id": user.id,
        "email": user.email
    }


# -----------------------------
# Task Routes
# -----------------------------

@app.get("/tasks")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks ORDER BY id"
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": row[2]
        }
        for row in rows
    ]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = %s",
        (task_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.title is None or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, done)
        VALUES (%s, %s)
        RETURNING id
        """,
        (task.title.strip(), False)
    )

    task_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": task_id,
        "title": task.title.strip(),
        "done": False
    }


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    if task.title is None or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET title = %s, done = %s
        WHERE id = %s
        RETURNING id, title, done
        """,
        (task.title.strip(), False, task_id)
    )

    row = cursor.fetchone()

    if row is None:
        connection.rollback()
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,)
    )

    if cursor.rowcount == 0:
        connection.rollback()
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    connection.commit()

    cursor.close()
    connection.close()

    return


# -----------------------------
# Database Initialization
# -----------------------------

initialize_database()