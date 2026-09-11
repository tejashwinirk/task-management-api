from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import initialize_database, get_connection

app = FastAPI()

initialize_database()

class TaskCreate(BaseModel):
    title: str | None = None

tasks = [
    {"id": 1, "title": "Learn FastAPI"},
    {"id": 2, "title": "Build CRUD API"},
    {"id": 3, "title": "Test the API"}
]


@app.get("/")
def root():
    return {"message": "Task API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

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
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )

    connection.commit()

    new_task_id = cursor.lastrowid

    connection.close()

    return {
        "id": new_task_id,
        "title": task.title,
        "done": False
    }

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task.title, 0, task_id)
    )

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()

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
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()
    connection.close()

    return