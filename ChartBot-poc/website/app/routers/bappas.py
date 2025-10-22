from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

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
async def create_bappas_request(request: BappasRequest):
    # Simulate Bappas website functionality
    # In real implementation, this would integrate with actual Bappas system
    
    return BappasResponse(
        request_id=f"BAPPAS_{hash(request.user_lan_id + request.ad_group_name)}",
        status="SUBMITTED",
        message=f"Request to {request.action} {request.ad_group_name} for {request.user_lan_id} has been submitted for approval"
    )

@router.get("/requests/{user_lan_id}")
async def get_user_requests(user_lan_id: str):
    # Return mock pending requests
    return {
        "pending_requests": [
            {
                "request_id": "BAPPAS_123",
                "ad_group": "det_developers",
                "status": "PENDING_APPROVAL",
                "requested_date": "2024-01-15"
            }
        ]
    }