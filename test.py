import jwt
import uvicorn
import mysql.connector
from fastapi import FastAPI, Depends, Body, HTTPException, Request, status, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from passlib.context import CryptContext  # For password hashing
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from src.database import Database


# Setting class
class Settings:
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins
    COOKIE_NAME = "access_token"


# User class
class User:
    def __init__(self, id, username, hashed_password):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password


# Task class
class Task:
    def __init__(self, id, user_id, description, is_done):
        self.id = id
        self.user_id = user_id
        self.description = description
        self.is_done = is_done


app = FastAPI()
app.mount("/static", StaticFiles(directory="src/WEB"), name="static")
templates = Jinja2Templates(directory="src/WEB/resources/views")
settings = Settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 for authentication (replace with your token-based authentication if needed)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# MySQL config
db_config = {
    "host": "localhost",
    "user": "admin",
    "password": "123456",
    "database": "todo_list",
}


# Dependency for getting the database connection (if using a database)
def get_db():
    db = Database(**db_config)
    try:
        yield db
    finally:
        db.close()  # Close the connection after each request


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_user_by_username(username: str):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        sql = "SELECT id, username, hashed_password FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        return User(*user) if user else None
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        return False


def decode_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    token = token.removeprefix("Bearer").strip()
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as e:
        return False

    user = get_user_by_username(username)
    return user


def get_current_user(request: Request) -> User:
    """
    Get the current user from the cookies in a request.

    Use this function from inside other routes to get the current user. Good
    for views that should work for both logged in, and not logged in users.
    """
    token = request.cookies.get(settings.COOKIE_NAME)
    if token is None:
        return False

    user = decode_token(token)
    return user


def first_get_tasks(user_id: int):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        sql = "SELECT * FROM tasks WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        tasks = cursor.fetchall()
        cursor.close()
        db.close()
        return [Task(*task) for task in tasks]
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        return False


# Root endpoint (can be updated to display tasks based on login status)
# @app.get("/")
# async def root(request: Request, current_user: User = Depends(get_current_user)):
#     print(current_user)
#     if not current_user:  # Check if user is logged in
#         return templates.TemplateResponse("register.html", {"request": request})
#     # tasks = await get_tasks(current_user=current_user)  # Get tasks for logged-in user
#     return templates.TemplateResponse("index.html", {"request": request, "username": current_user.username})
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/todo_list")
async def todo_interface(request: Request, current_user: User = Depends(get_current_user)):
    # tasks = await get_tasks(current_user=current_user)  # Get tasks for logged-in user
    return templates.TemplateResponse("index.html", {"request": request, "username": current_user.username})


@app.get("/login")
async def login_interface(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_interface(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Function to verify user password (replace with actual hashing logic)
async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/login")
async def login(
    response: Response,
    username: str = Body(...),
    password: str = Body(...),
):
    user = get_user_by_username(username=username)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(data={"username": user.username})

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=settings.COOKIE_NAME, value=f"Bearer {access_token}", httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


# Function to hash a password (for registration)
def hash_password(password):
    return pwd_context.hash(password)


# Register endpoint
@app.post("/register")
async def register(
    username: str = Body(...), password: str = Body(...), db: Database = Depends(get_db)
):
    existing_user = get_user_by_username(username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(password)
    # Save user to database (replace with actual database access)
    # if not get_db:  # No database, skip saving
    #     return {"message": "User registered successfully (without database)"}
    if not db:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    db.create_user(username, hashed_password)
    return {"message": "User registered successfully"}


# Endpoint to get all tasks for the current user
@app.get("/api/tasks")
async def get_tasks(
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    tasks = db.get_tasks(current_user.id)
    return [Task(*task) for task in tasks]  # Convert database rows to Task objects


# Endpoint to create a new task
@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    task: dict,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    db.insert_task(current_user.id, task["description"])
    return {"message": "Task created successfully"}


# Endpoint to update a task (including marking completion)
@app.patch("/api/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_update: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    if not db.update_task(current_user.id, task_id, task_update):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task updated successfully"}


# Endpoint to delete a task
@app.delete("/api/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
    if not db.delete_task(current_user.id, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@app.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


# Run the application (optional, for development purposes)
if __name__ == "__main__":
    uvicorn.run("test:app", host="127.0.0.1", port=8000, reload=True)
