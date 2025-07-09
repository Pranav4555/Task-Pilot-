# tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from typing import List

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_task = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.Task])
def get_my_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    shared = db.query(models.TaskUserAssociation).filter(models.TaskUserAssociation.user_id == current_user.id).all()
    shared_tasks = [assoc.task for assoc in shared]
    return tasks + shared_tasks

@router.get("/shared/dashboard", response_model=List[schemas.Task])
def shared_task_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    shared_assocs = db.query(models.TaskUserAssociation).filter_by(user_id=current_user.id).all()
    shared_tasks = []
    for assoc in shared_assocs:
        task_data = assoc.task
        task_data.role = assoc.role  # dynamically attach current user's role for this task
        shared_tasks.append(task_data)
    return shared_tasks

@router.get("/{task_id}", response_model=schemas.Task)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["viewer", "editor", "owner"])
    return task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["editor", "owner"])
    for key, value in updated_task.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["owner"])
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

@router.post("/{task_id}/share")
def share_task(task_id: int, collaborator: schemas.Collaborator, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if collaborator.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot share task with yourself")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["owner"])

    existing = db.query(models.TaskUserAssociation).filter_by(task_id=task.id, user_id=collaborator.user_id).first()
    if existing:
        existing.role = collaborator.role  # Update existing role
    else:
        assoc = models.TaskUserAssociation(task_id=task.id, user_id=collaborator.user_id, role=collaborator.role)
        db.add(assoc)
    db.commit()
    return {"detail": f"Shared with user {collaborator.user_id} as {collaborator.role}"}

@router.post("/{task_id}/unshare")
def unshare_task(task_id: int, collaborator: schemas.Collaborator, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if collaborator.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot unshare yourself (owner)")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["owner"])

    assoc = db.query(models.TaskUserAssociation).filter_by(task_id=task.id, user_id=collaborator.user_id).first()
    if assoc:
        db.delete(assoc)
        db.commit()
    return {"detail": f"Access revoked from user {collaborator.user_id}"}

@router.put("/{task_id}/role")
def update_role(task_id: int, collaborator: schemas.Collaborator, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if collaborator.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot update your own role")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    auth.check_user_permission(task, current_user, required_roles=["owner"])

    assoc = db.query(models.TaskUserAssociation).filter_by(task_id=task.id, user_id=collaborator.user_id).first()
    if not assoc:
        raise HTTPException(status_code=404, detail="User is not a collaborator")
    assoc.role = collaborator.role
    db.commit()
    return {"detail": f"Updated role for user {collaborator.user_id} to {collaborator.role}"}
