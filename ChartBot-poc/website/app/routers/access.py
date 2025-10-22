from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/user/{lan_id}")
async def get_user_access(lan_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.lan_id == lan_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    access_records = db.query(models.UserProjectAccess).filter(
        models.UserProjectAccess.user_id == user.user_id,
        models.UserProjectAccess.status == "ACTIVE"
    ).all()
    
    projects = []
    for access in access_records:
        project = db.query(models.Project).filter(
            models.Project.project_id == access.project_id
        ).first()
        if project:
            projects.append({
                "project_name": project.project_name,
                "access_type": access.access_type,
                "effective_from": access.effective_from
            })
    
    return {
        "user": {
            "lan_id": user.lan_id,
            "full_name": user.full_name,
            "email": user.email
        },
        "projects": projects
    }