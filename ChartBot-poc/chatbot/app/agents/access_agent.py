from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from ..models import User, Project, AdGroup, UserProjectAssignment, UserAdGroupAccess, AdGroupAccessRequest, AccessHistory, SystemApprover, NotificationQueue

class AccessControlAgent:
    def __init__(self, db: Session):
        self.db = db

    def find_user_by_name(self, full_name: str) -> List[User]:
        return self.db.query(User).filter(
            User.full_name.ilike(f"%{full_name}%")
        ).all()

    def get_user_by_lan_id(self, lan_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.lan_id == lan_id).first()

    def create_user(self, lan_id: str, full_name: str, email: str = None) -> User:
        # Extract first and last name from full name
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        user = User(
            lan_id=lan_id, 
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            email=email or f"{lan_id}@example.com"
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_project_by_name(self, project_name: str) -> Optional[Project]:
        return self.db.query(Project).filter(
            Project.project_name.ilike(f"%{project_name}%")
        ).first()

    def get_ad_groups_for_project(self, project_id: int) -> List[AdGroup]:
        return self.db.query(AdGroup).filter(
            AdGroup.project_id == project_id,
            AdGroup.is_active == True
        ).all()

    def get_user_project_assignment(self, user_id: int, project_id: int) -> Optional[UserProjectAssignment]:
        return self.db.query(UserProjectAssignment).filter(
            and_(
                UserProjectAssignment.user_id == user_id,
                UserProjectAssignment.project_id == project_id,
                UserProjectAssignment.is_current == True
            )
        ).first()

    def onboard_user_to_projects(self, user_lan_id: str, full_name: str,
                               projects: List[str], requested_by: str) -> Dict[str, Any]:
        try:
            # Find or create user
            user = self.get_user_by_lan_id(user_lan_id)
            if not user:
                user = self.create_user(user_lan_id, full_name)

            results = []
            for project_name in projects:
                project = self.get_project_by_name(project_name)
                if project:
                    # Check if assignment already exists
                    existing_assignment = self.get_user_project_assignment(user.user_id, project.project_id)
                    if not existing_assignment:
                        # Create assignment record
                        assignment = UserProjectAssignment(
                            user_id=user.user_id,
                            project_id=project.project_id,
                            requested_by=requested_by
                        )
                        self.db.add(assignment)
                        results.append(f"Added to {project.project_name}")

                        # Log to access history
                        self.log_access_history(
                            user.user_id,
                            None,  # No specific AD group for project assignment
                            "request",
                            requested_by,
                            f"Project assignment to {project.project_name}"
                        )

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
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    def request_project_access(self, user_lan_id: str, project_name: str,
                             requested_by: str) -> Dict[str, Any]:
        try:
            user = self.get_user_by_lan_id(user_lan_id)
            if not user:
                return {"status": "error", "message": "User not found"}

            project = self.get_project_by_name(project_name)
            if not project:
                return {"status": "error", "message": "Project not found"}

            # Get AD groups for the project
            ad_groups = self.get_ad_groups_for_project(project.project_id)
            
            if not ad_groups:
                return {"status": "error", "message": "No AD groups found for this project"}

            # Create access requests for each AD group
            request_results = []
            for ad_group in ad_groups:
                # Check if access already exists
                existing_access = self.db.query(UserAdGroupAccess).filter(
                    and_(
                        UserAdGroupAccess.user_id == user.user_id,
                        UserAdGroupAccess.adgroup_id == ad_group.adgroup_id,
                        UserAdGroupAccess.access_granted == True
                    )
                ).first()

                if not existing_access:
                    # Create access request
                    access_request = AdGroupAccessRequest(
                        user_id=user.user_id,
                        adgroup_id=ad_group.adgroup_id,
                        request_type="grant",
                        request_source="chatbot",
                        requester_lanid=requested_by,
                        comments=f"Access request via chatbot for {project.project_name}"
                    )
                    self.db.add(access_request)
                    request_results.append(ad_group.adgroup_name)

                    # Add to notification queue for approvers
                    self.add_notification_for_approvers(ad_group, user, project, "grant")

            self.db.commit()

            # Log to access history
            self.log_access_history(
                user.user_id,
                None,
                "request",
                requested_by,
                f"Access request for {project.project_name} ({len(request_results)} AD groups)"
            )

            return {
                "status": "success",
                "message": f"Access requested for {project.project_name}",
                "ad_groups": len(request_results),
                "details": f"Requests created for: {', '.join(request_results)}"
            }
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    def revoke_project_access(self, user_lan_id: str, project_name: str,
                            requested_by: str) -> Dict[str, Any]:
        try:
            user = self.get_user_by_lan_id(user_lan_id)
            if not user:
                return {"status": "error", "message": "User not found"}

            project = self.get_project_by_name(project_name)
            if not project:
                return {"status": "error", "message": "Project not found"}

            # Get AD groups for the project
            ad_groups = self.get_ad_groups_for_project(project.project_id)
            
            # Find active access records to revoke
            revoked_groups = []
            for ad_group in ad_groups:
                active_access = self.db.query(UserAdGroupAccess).filter(
                    and_(
                        UserAdGroupAccess.user_id == user.user_id,
                        UserAdGroupAccess.adgroup_id == ad_group.adgroup_id,
                        UserAdGroupAccess.access_granted == True
                    )
                ).first()

                if active_access:
                    # Revoke access
                    active_access.access_granted = False
                    active_access.revoke_date = datetime.now()
                    revoked_groups.append(ad_group.adgroup_name)

                    # Create revocation request
                    revoke_request = AdGroupAccessRequest(
                        user_id=user.user_id,
                        adgroup_id=ad_group.adgroup_id,
                        request_type="revoke",
                        request_source="chatbot",
                        requester_lanid=requested_by,
                        comments=f"Access revocation via chatbot for {project.project_name}"
                    )
                    self.db.add(revoke_request)

                    # Add to notification queue
                    self.add_notification_for_approvers(ad_group, user, project, "revoke")

                    # Log to access history
                    self.log_access_history(
                        user.user_id,
                        ad_group.adgroup_id,
                        "revoke",
                        requested_by,
                        f"Access revoked for {ad_group.adgroup_name}"
                    )

            # Update project assignment if exists
            assignment = self.get_user_project_assignment(user.user_id, project.project_id)
            if assignment:
                assignment.is_current = False
                assignment.end_date = datetime.now().date()

            self.db.commit()

            return {
                "status": "success",
                "message": f"Access revoked for {project.project_name}",
                "ad_groups": len(revoked_groups),
                "details": f"Access revoked for: {', '.join(revoked_groups)}"
            }
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    def add_notification_for_approvers(self, ad_group: AdGroup, user: User, project: Project, action: str):
        """Add notifications for approvers"""
        if ad_group.approver_lanids:
            approver_lanids = [lanid.strip() for lanid in ad_group.approver_lanids.split(',')]
            for lanid in approver_lanids:
                notification = NotificationQueue(
                    recipient_lanid=lanid,
                    message_title=f"Access {action.capitalize()} Request",
                    message_body=f"User {user.full_name} ({user.lan_id}) requested {action} access for {ad_group.adgroup_name} in {project.project_name}",
                    status="pending"
                )
                self.db.add(notification)

    def log_access_history(self, user_id: int, adgroup_id: Optional[int], action: str, action_by: str, comments: str):
        """Log actions to access history"""
        history = AccessHistory(
            user_id=user_id,
            adgroup_id=adgroup_id,
            action=action,
            action_by=action_by,
            comments=comments
        )
        self.db.add(history)

    def log_audit(self, action_type: str, user_lan_id: str, project_code: str,
                 ad_groups: str, performed_by: str, status: str):
        """Legacy audit log - can be enhanced or integrated with AccessHistory"""
        # This can be integrated with the new AccessHistory table
        pass

    def get_user_access_summary(self, user_lan_id: str) -> Dict[str, Any]:
        user = self.get_user_by_lan_id(user_lan_id)
        if not user:
            return {"status": "error", "message": "User not found"}

        # Get current project assignments
        assignments = self.db.query(UserProjectAssignment).filter(
            and_(
                UserProjectAssignment.user_id == user.user_id,
                UserProjectAssignment.is_current == True
            )
        ).all()

        # Get active AD group access
        active_access = self.db.query(UserAdGroupAccess).filter(
            and_(
                UserAdGroupAccess.user_id == user.user_id,
                UserAdGroupAccess.access_granted == True
            )
        ).all()

        projects = []
        for assignment in assignments:
            project = self.db.query(Project).filter(
                Project.project_id == assignment.project_id
            ).first()
            if project:
                projects.append({
                    "project_name": project.project_name,
                    "assignment_start": assignment.start_date,
                    "is_current": assignment.is_current
                })

        ad_groups = []
        for access in active_access:
            ad_group = self.db.query(AdGroup).filter(
                AdGroup.adgroup_id == access.adgroup_id
            ).first()
            if ad_group:
                project = self.db.query(Project).filter(
                    Project.project_id == ad_group.project_id
                ).first()
                ad_groups.append({
                    "ad_group_name": ad_group.adgroup_name,
                    "project_name": project.project_name if project else "Unknown",
                    "grant_date": access.grant_date
                })

        return {
            "user": {
                "lan_id": user.lan_id,
                "full_name": user.full_name,
                "email": user.email
            },
            "projects": projects,
            "ad_groups": ad_groups
        }