from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, UserProjectAccess, Project

router = APIRouter()

@router.get("/user/{lan_id}")
async def get_user_access(lan_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Check permissions
    if current_user["role"] not in ["admin", "hr"] and current_user["lan_id"] != lan_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.lan_id == lan_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_records = db.query(UserProjectAccess).filter(
        UserProjectAccess.user_id == user.user_id,
        UserProjectAccess.status == "ACTIVE"
    ).all()

    projects = []
    for access in access_records:
        project = db.query(Project).filter(
            Project.project_id == access.project_id
        ).first()
        if project:
            projects.append({
                "project_code": project.project_code,
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

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    users = db.query(User).filter(User.is_active == True).all()
    return users