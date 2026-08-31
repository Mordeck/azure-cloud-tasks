from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException

# importacion de fast api para levantar el servicio api

from sqlalchemy.orm import Session

#importacion 
from . import models
from . import schemas
from .database import engine
from .database import get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Cloud Tasks API",
    description="API REST desplegada en Microsoft Azure",
    version="1.0.0"
)


@app.get("/")
def root():

    return {
        "message": "Cloud Tasks API",
        "cloud": "Microsoft Azure"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post(
    "/tasks",
    response_model=schemas.TaskResponse,
    status_code=201
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):

    new_task = models.Task(
        title=task.title,
        description=task.description
    )

    db.add(new_task)

    db.commit()

    db.refresh(new_task)

    return new_task


@app.get(
    "/tasks",
    response_model=list[schemas.TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Task
    ).all()


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(
        models.Task
    ).filter(
        models.Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse
)
def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):

    task = db.query(
        models.Task
    ).filter(
        models.Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            task,
            field,
            value
        )

    db.commit()

    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(
        models.Task
    ).filter(
        models.Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)

    db.commit()

    return {
        "message": "Task deleted"
    }