from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas import CreateTask, UpdateTask
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from sqlalchemy import insert, select, update, delete

task_router = APIRouter(prefix="/task", tags=["task"])


@task_router.get("/")
async def all_task(db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task)).scalars().all()
    return tasks


@task_router.get("/{task_id}")
async def task_by_id(db: Annotated[Session, Depends(get_db)],
                     task_id: int):
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    else:
        return task


@task_router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)],
                      user_id: int,
                      task: CreateTask):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.execute(insert(Task).values(title=task.title,
                                   content=task.content,
                                   priority=task.priority,
                                   user_id=user_id))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Task create is successful!'}


@task_router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int,
                      task: UpdateTask):
    result = db.execute(update(Task).where(Task.id == task_id).values(title=task.title,
                                                                      content=task.content,
                                                                      priority=task.priority))
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Task update is successful!'}


@task_router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)],
                      task_id: int):
    result = db.execute(delete(Task).where(Task.id == task_id))
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Task not found")
    db.commit()
    return {'status_code': status.HTTP_200_OK,
            'transaction': 'Task delete is successful!'}
