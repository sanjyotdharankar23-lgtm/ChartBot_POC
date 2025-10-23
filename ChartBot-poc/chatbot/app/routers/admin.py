from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth import require_admin
from ..models import AccessRequest, User, Project, ADGroup
from ..schemas import AccessRequestResponse

router = APIRouter()

@router.get("/pending-requests", response_model=List[AccessRequestResponse])
async def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    requests = db.query(AccessRequest).filter(
        AccessRequest.request_status == "PENDING"
    ).all()
    return requests

@router.post("/approve-request/{request_id}")
async def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    access_request = db.query(AccessRequest).filter(
        AccessRequest.request_id == request_id
    ).first()
    
    if not access_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    access_request.request_status = "APPROVED"
    access_request.approved_by = current_user["username"]
    access_request.approval_date = datetime.now()
    
    # If it's a grant request, create the access record
    if access_request.request_type == "GRANT":
        user_project_access = UserProjectAccess(
            user_id=access_request.user_id,
            project_id=access_request.project_id,
            access_type="MEMBER",
            requested_by=access_request.requested_by
        )
        db.add(user_project_access)
    
    db.commit()
    
    return {"status": "success", "message": "Request approved"}

@router.get("/audit-logs")
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    logs = db.query(AuditLog).order_by(AuditLog.performed_at.desc()).limit(100).all()
    return logs