from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.models.classes import User

router = APIRouter()

# User CREATE
@router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# User READ ALL
@router.get("/", response_model=List[UserRead])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# User READ SPECIFIC
@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# User UPDATE
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# User DELETE
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None
