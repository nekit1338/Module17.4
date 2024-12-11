from fastapi import FastAPI
from app.models import User, Task
from routers.task import task_router
from routers.user import user_router
import uvicorn
from app.backend.db import engine, Base

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to Taskmanager"}


app.include_router(task_router)
app.include_router(user_router)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)
