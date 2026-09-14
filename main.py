from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from database import initialize_database, get_connection, supabase

app = FastAPI()

security = HTTPBearer(auto_error=False)

initialize_database()


class TaskCreate(BaseModel):
    title: str | None = None


class AuthRequest(BaseModel):
    email: str
    password: str


@app.get("/")
def root():
    return {"message": "Task API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/signup", status_code=201)
def signup(auth: AuthRequest):
    if not auth.email.strip() or not auth.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_up({
            "email": auth.email,
            "password": auth.password
        })

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
def login(auth: AuthRequest):
    if not auth.email.strip() or not auth.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth.email,
            "password": auth.password
        })

        if response.session is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid login credentials"
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )


@app.get("/public/info")
def public_info():
    return {
        "message": "This is a public endpoint"
    }


@app.get("/protected/profile")
def protected_profile(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    return {
        "message": "Protected profile endpoint"
    }


@app.get("/tasks")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {"id": row[0], "title": row[1], "done": bool(row[2])}
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
        "done": bool(row[2])
    }


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (task.title, False)
    )

    new_task_id = cursor.fetchone()[0]

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "id": new_task_id,
        "title": task.title,
        "done": False
    }


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (task.title, False, task_id)
    )

    if cursor.rowcount == 0:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    connection.commit()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = %s",
        (task_id,)
    )
    row = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
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