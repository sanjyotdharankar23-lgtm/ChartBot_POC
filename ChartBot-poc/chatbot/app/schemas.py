from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    lan_id: str
    full_name: str
    email: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    project_name: str
    description: Optional[str] = None
    is_active: bool = True

class ProjectResponse(ProjectBase):
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ADGroupBase(BaseModel):
    project_id: int
    ad_group_name: str
    approver_email: str
    approver_lan_id: str
    is_access_group: bool = True

class ADGroupResponse(ADGroupBase):
    ad_group_id: int
    
    class Config:
        from_attributes = True

class AccessRequest(BaseModel):
    user_lan_id: str
    project_name: str
    action: str  # 'grant' or 'revoke'

class ChatMessage(BaseModel):
    message: str
    user_role: str = "user"

class ChatResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None
    requires_confirmation: bool = False