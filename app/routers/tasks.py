from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.models.classes import Task, User

router = APIRouter()

# Task CREATE
@router.post("/", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    # Verify user exists
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for unique idm_key if provided
    if task.idm_key:
        existing_task = db.query(Task).filter(Task.idm_key == task.idm_key).first()
        if existing_task:
            return existing_task
    
    # Create new task
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Task READ ALL
@router.get("/", response_model=List[TaskRead])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks with pagination"""
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

# Task READ SPECIFIC
@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: UUID, db: Session = Depends(get_db)):
    """Get a specific task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Task UPDATE
@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: UUID, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

# Task DELETE
@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    """Delete a task"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return None

# Summary Endpoint for tasks by status
@router.get("/summary/status", response_model=dict)
def task_summary_by_status(db: Session = Depends(get_db)):
    """Get summary of tasks grouped by status"""
    summary = {}
    for status in [0, 1, 2]:  # 0: pending, 1: in progress, 2: completed
        count = db.query(Task).filter(Task.status == status).count()
        summary[status] = count
    return summary
