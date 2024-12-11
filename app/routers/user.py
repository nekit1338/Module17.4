from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()
    return users


@user_router.get("/{user_id}")
async def user_by_id(db: Annotated[Session, Depends(get_db)],
                     user_id: int):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")
    else:
        return user


@user_router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)],
                      user: CreateUser):
    existing_user = db.execute(select(User).where(User.username == user.username)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользоатель с таким именем уже существует")

    db.execute(insert(User).values(username=user.username,
                                   first_name=user.first_name,
                                   last_name=user.last_name,
                                   age=user.age))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'}


@user_router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      user: UpdateUser):
    result = db.execute(update(User).where(User.id == user_id).values(first_name=user.first_name,
                                                                      last_name=user.last_name,
                                                                      age=user.age))
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'User update is successful!'}


@user_router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)],
                      user_id: int):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")
    else:
        for task in user.tasks:
            db.delete(task)
        db.delete(user)
        db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'User and related tasks deleted successfully!'}


@user_router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)],
                           user_id: int):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User was not found")
    return user.tasks
