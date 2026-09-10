from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

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
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title
    }

    tasks.append(new_task)
    return new_task