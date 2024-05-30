import uvicorn
from fastapi import FastAPI, Depends, Body, HTTPException, Request
from starlette.status import HTTP_201_CREATED
from starlette.staticfiles import StaticFiles
from src.database import Database  # Import the Database class
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext  # For password hashing
import secrets  # For generating random secret key

app = FastAPI()

# Replace "static" with your actual directory path
app.mount("/static", StaticFiles(directory="src/WEB"), name="static")

templates = Jinja2Templates(
    directory="src/WEB/resources/views"
)  # Replace with your templates directory

# Replace with your MySQL connection details
MYSQL_HOST = "localhost"
MYSQL_USER = "admin"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "todo_list"


# Dependency for getting the database connection
def get_db():
    db = Database(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    try:
        yield db
    finally:
        db.close()  # Close the connection after each request


@app.get("/")
async def root(request: Request):  # Inject the request object
    return templates.TemplateResponse(
        "index.html", {"request": request, "data": []}
    )  # Replace with your data or logic


# User model (replace with your actual user model if needed)
class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Function to retrieve the current user (replace with your authentication logic)
async def get_current_user(db: Database = Depends(get_db)):
    # Implement logic to retrieve the current user based on a token or session (placeholder)
    return User(1, "placeholder_user")  # Replace with actual user data retrieval


# Task model
class Task:
    def __init__(self, id, user_id, description, is_done):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.is_done = is_done


# Endpoint to get all tasks for the current user
@app.get("/api/tasks")
async def get_tasks(
    db: Database = Depends(get_db), current_user: User = Depends(get_current_user)
):
    tasks = db.get_tasks(current_user.id)
    return [Task(*task) for task in tasks]  # Convert database rows to Task objects


# Endpoint to create a new task
@app.post("/api/tasks", status_code=HTTP_201_CREATED)
async def create_task(
    task: dict,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.insert_task(current_user.id, task["description"])
    return {"message": "Task created successfully"}


# Endpoint to update a task (including marking completion)
@app.patch("/api/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: dict,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.update_task(current_user.id, task_id, task_update):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}


# Endpoint to delete a task
@app.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.delete_task(current_user.id, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# Run the application (optional, for development purposes)
if __name__ == "__main__":
    uvicorn.run("main_copy:app", host="0.0.0.0", port=8000, reload=True)
