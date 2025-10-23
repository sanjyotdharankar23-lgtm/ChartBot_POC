from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import AccessRequest, User, ADGroup, Project

router = APIRouter()

class BappasRequest(BaseModel):
    user_lan_id: str
    ad_group_name: str
    action: str  # grant or revoke

class BappasResponse(BaseModel):
    request_id: str
    status: str
    message: str

@router.post("/request", response_model=BappasResponse)
async def create_bappas_request(
    request: BappasRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Find user
    user = db.query(User).filter(User.lan_id == request.user_lan_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find AD group
    ad_group = db.query(ADGroup).filter(ADGroup.ad_group_name == request.ad_group_name).first()
    if not ad_group:
        raise HTTPException(status_code=404, detail="AD Group not found")

    # Create access request
    access_request = AccessRequest(
        user_id=user.user_id,
        project_id=ad_group.project_id,
        ad_group_id=ad_group.ad_group_id,
        request_type=request.action.upper(),
        requested_by=current_user["username"],
        comments=f"Request via Bappas website for {request.action} access"
    )
    
    db.add(access_request)
    db.commit()
    db.refresh(access_request)

    return BappasResponse(
        request_id=f"BAPPAS_{access_request.request_id}",
        status="SUBMITTED",
        message=f"Request to {request.action} {request.ad_group_name} for {request.user_lan_id} has been submitted for approval"
    )

@router.get("/requests/{user_lan_id}")
async def get_user_requests(user_lan_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "hr"] and current_user["lan_id"] != user_lan_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db.query(User).filter(User.lan_id == user_lan_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    requests = db.query(AccessRequest).filter(
        AccessRequest.user_id == user.user_id
    ).order_by(AccessRequest.created_at.desc()).limit(50).all()

    result = []
    for req in requests:
        project = db.query(Project).filter(Project.project_id == req.project_id).first()
        ad_group = db.query(ADGroup).filter(ADGroup.ad_group_id == req.ad_group_id).first()
        
        result.append({
            "request_id": req.request_id,
            "project_name": project.project_name if project else "Unknown",
            "ad_group": ad_group.ad_group_name if ad_group else "Unknown",
            "request_type": req.request_type,
            "status": req.request_status,
            "requested_date": req.created_at,
            "approved_by": req.approved_by
        })

    return {"pending_requests": result}