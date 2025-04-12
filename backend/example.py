from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4, UUID

app = FastAPI(
    title="To-Do API",
    description="A simple and clean To-Do application built with FastAPI. Allows creating, reading, updating, and deleting to-do tasks.",
    version="1.0.0"
)

# ---------------------------
# Pydantic Models (Schemas)
# ---------------------------

class ToDoCreate(BaseModel):
    """
    Schema for creating a new to-do item.
    """
    title: str
    description: Optional[str] = None
    completed: bool = False

class ToDo(ToDoCreate):
    """
    Schema for a to-do item, including a unique identifier.
    """
    id: UUID

# ---------------------------
# In-memory data storage
# ---------------------------

todos: List[ToDo] = []

# ---------------------------
# Routes
# ---------------------------

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint for health check or welcome message.
    
    Returns a simple JSON message indicating the API is working.
    """
    return {"message": "Welcome to the To-Do API!"}

@app.get("/todos", response_model=List[ToDo], tags=["To-Dos"])
def get_all_todos():
    """
    Retrieve all to-do items.

    Returns:
        A list of all to-do tasks currently stored in memory.
    """
    return todos

@app.post("/todos", response_model=ToDo, status_code=201, tags=["To-Dos"])
def create_todo(todo: ToDoCreate):
    """
    Create a new to-do item.

    Args:
        todo (ToDoCreate): The to-do item to be created.

    Returns:
        The newly created to-do item with a unique UUID.
    """
    new_todo = ToDo(id=uuid4(), **todo.dict())
    todos.append(new_todo)
    return new_todo

@app.get("/todos/{todo_id}", response_model=ToDo, tags=["To-Dos"])
def get_todo(todo_id: UUID):
    """
    Retrieve a single to-do item by its UUID.

    Args:
        todo_id (UUID): The unique identifier of the to-do item.

    Returns:
        The to-do item matching the given UUID.

    Raises:
        HTTPException: If no item with the given UUID is found.
    """
    for todo in todos:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="To-Do not found")

@app.put("/todos/{todo_id}", response_model=ToDo, tags=["To-Dos"])
def update_todo(todo_id: UUID, updated_todo: ToDoCreate):
    """
    Update an existing to-do item.

    Args:
        todo_id (UUID): The UUID of the to-do item to update.
        updated_todo (ToDoCreate): The updated task data.

    Returns:
        The updated to-do item.

    Raises:
        HTTPException: If the to-do item does not exist.
    """
    for idx, todo in enumerate(todos):
        if todo.id == todo_id:
            todos[idx] = ToDo(id=todo_id, **updated_todo.dict())
            return todos[idx]
    raise HTTPException(status_code=404, detail="To-Do not found")

@app.delete("/todos/{todo_id}", status_code=204, tags=["To-Dos"])
def delete_todo(todo_id: UUID):
    """
    Delete a to-do item by its UUID.

    Args:
        todo_id (UUID): The unique identifier of the to-do item to delete.

    Returns:
        No content if deletion is successful.

    Raises:
        HTTPException: If the to-do item does not exist.
    """
    for idx, todo in enumerate(todos):
        if todo.id == todo_id:
            todos.pop(idx)
            return
    raise HTTPException(status_code=404, detail="To-Do not found")
