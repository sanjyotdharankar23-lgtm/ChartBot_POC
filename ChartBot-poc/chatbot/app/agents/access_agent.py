from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..models import User, Project, ADGroup, UserProjectAccess, AuditLog
from ..schemas import AccessRequest
import requests

class AccessControlAgent:
    def __init__(self, db: Session):
        self.db = db
    
    def find_user_by_name(self, full_name: str) -> List[User]:
        return self.db.query(User).filter(
            User.full_name.ilike(f"%{full_name}%")
        ).all()
    
    def get_user_by_lan_id(self, lan_id: str) -> User:
        return self.db.query(User).filter(User.lan_id == lan_id).first()
    
    def create_user(self, lan_id: str, full_name: str, email: str = None) -> User:
        user = User(lan_id=lan_id, full_name=full_name, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_project(self, project_name: str) -> Project:
        return self.db.query(Project).filter(
            Project.project_name == project_name
        ).first()
    
    def get_ad_groups_for_project(self, project_id: int) -> List[ADGroup]:
        return self.db.query(ADGroup).filter(
            ADGroup.project_id == project_id
        ).all()
    
    def onboard_user_to_projects(self, user_lan_id: str, full_name: str, 
                               projects: List[str], requested_by: str) -> Dict[str, Any]:
        # Find or create user
        user = self.get_user_by_lan_id(user_lan_id)
        if not user:
            user = self.create_user(user_lan_id, full_name)
        
        results = []
        for project_name in projects:
            project = self.get_project(project_name)
            if project:
                # Create access record
                access = UserProjectAccess(
                    user_id=user.user_id,
                    project_id=project.project_id,
                    access_type="GRANTED",
                    requested_by=requested_by
                )
                self.db.add(access)
                results.append(f"Added to {project_name}")
        
        self.db.commit()
        
        # Log audit
        self.log_audit(
            "ONBOARD_USER",
            user_lan_id,
            ",".join(projects),
            ",".join(results),
            requested_by,
            "COMPLETED"
        )
        
        return {"status": "success", "results": results}
    
    def request_project_access(self, user_lan_id: str, project_name: str, 
                             requested_by: str) -> Dict[str, Any]:
        user = self.get_user_by_lan_id(user_lan_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        project = self.get_project(project_name)
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        # Check if access already exists
        existing_access = self.db.query(UserProjectAccess).filter(
            UserProjectAccess.user_id == user.user_id,
            UserProjectAccess.project_id == project.project_id,
            UserProjectAccess.status == "ACTIVE"
        ).first()
        
        if existing_access:
            return {"status": "info", "message": "Access already exists"}
        
        # Create access request
        access = UserProjectAccess(
            user_id=user.user_id,
            project_id=project.project_id,
            access_type="REQUESTED",
            requested_by=requested_by
        )
        self.db.add(access)
        self.db.commit()
        
        # Simulate Bappas API call
        bappas_result = self.call_bappas_api(user_lan_id, project_name, "grant")
        
        # Log audit
        self.log_audit(
            "REQUEST_ACCESS",
            user_lan_id,
            project_name,
            f"Bappas result: {bappas_result}",
            requested_by,
            "REQUESTED"
        )
        
        return {
            "status": "success", 
            "message": f"Access requested for {project_name}",
            "bappas_result": bappas_result
        }
    
    def revoke_project_access(self, user_lan_id: str, project_name: str,
                            requested_by: str) -> Dict[str, Any]:
        user = self.get_user_by_lan_id(user_lan_id)
        if not user:
            return {"status": "error", "message": "User not found"}
        
        project = self.get_project(project_name)
        if not project:
            return {"status": "error", "message": "Project not found"}
        
        # Find active access records
        active_access = self.db.query(UserProjectAccess).filter(
            UserProjectAccess.user_id == user.user_id,
            UserProjectAccess.project_id == project.project_id,
            UserProjectAccess.status == "ACTIVE"
        ).all()
        
        if not active_access:
            return {"status": "info", "message": "No active access found"}
        
        # Revoke access
        for access in active_access:
            access.status = "REVOKED"
            access.effective_to = func.now()
        
        self.db.commit()
        
        # Simulate Bappas API call for revocation
        bappas_result = self.call_bappas_api(user_lan_id, project_name, "revoke")
        
        # Log audit
        self.log_audit(
            "REVOKE_ACCESS",
            user_lan_id,
            project_name,
            f"Bappas result: {bappas_result}",
            requested_by,
            "REVOKED"
        )
        
        return {
            "status": "success",
            "message": f"Access revoked for {project_name}",
            "bappas_result": bappas_result
        }
    
    def call_bappas_api(self, user_lan_id: str, project_name: str, action: str) -> str:
        # Simulate Bappas website API call
        try:
            # In real implementation, this would call the actual Bappas API
            ad_groups = self.get_ad_groups_for_project(
                self.get_project(project_name).project_id
            )
            
            for ad_group in ad_groups:
                # Simulate API call for each AD group
                pass
            
            return f"Bappas {action} request submitted for {len(ad_groups)} AD groups"
        except Exception as e:
            return f"Bappas API error: {str(e)}"
    
    def log_audit(self, action_type: str, user_lan_id: str, project_code: str,
                 ad_groups: str, performed_by: str, status: str):
        audit_log = AuditLog(
            action_type=action_type,
            user_lan_id=user_lan_id,
            project_code=project_code,
            ad_groups=ad_groups,
            performed_by=performed_by,
            status=status
        )
        self.db.add(audit_log)
        self.db.commit()