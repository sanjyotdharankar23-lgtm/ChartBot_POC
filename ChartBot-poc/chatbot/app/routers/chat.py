from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..schemas import ChatMessage, ChatResponse
from ..agents.nlp_processor import NLPProcessor
from ..agents.access_agent import AccessControlAgent
import re

router = APIRouter()
nlp_processor = NLPProcessor()

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(
    message: ChatMessage,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Process natural language
        nlp_result = nlp_processor.process_message(
            message.message,
            current_user["role"]
        )

        agent = AccessControlAgent(db)
        response_text = ""
        action_taken = None
        user_info = None
        project_info = None

        print(f"NLP Result: {nlp_result}")  # Debug log

        # Handle different actions based on NLP result
        action = nlp_result.get("action", "unknown")
        user_lan_id = nlp_result.get("user_lan_id")
        project = nlp_result.get("project")

        # If user_lan_id not detected, try to extract from message
        if not user_lan_id and current_user["role"] in ["admin", "hr"]:
            user_info = nlp_processor.extract_user_info(message.message)
            user_lan_id = user_info.get('lan_id')

        # If project not detected, try to extract from message
        if not project:
            projects = nlp_processor.extract_projects_from_text(message.message)
            if projects:
                project = projects[0]  # Use first detected project

        # Use current user's LAN ID for user-specific actions
        if not user_lan_id and current_user["role"] == "user":
            user_lan_id = current_user["lan_id"]

        if action == "onboard_user" and current_user["role"] in ["admin", "hr"]:
            if not user_lan_id:
                return ChatResponse(
                    response="I need the user's LAN ID to onboard them. Please provide the LAN ID.",
                    requires_confirmation=False
                )

            projects = nlp_processor.extract_projects_from_text(message.message)
            if not projects:
                return ChatResponse(
                    response="I need to know which projects to onboard the user to. Please specify projects like DET, CART, OAP etc.",
                    requires_confirmation=False
                )

            user_info = nlp_processor.extract_user_info(message.message)
            full_name = user_info.get('full_name', 'Unknown User')

            result = agent.onboard_user_to_projects(
                user_lan_id,
                full_name,
                projects,
                current_user["username"]
            )
            response_text = f"User onboarding completed: {result['results']}"
            action_taken = "onboard_user"

        elif action == "grant_access":
            if not user_lan_id:
                return ChatResponse(
                    response="I need to know which user to grant access for. Please provide the LAN ID or full name.",
                    requires_confirmation=False
                )

            if not project:
                return ChatResponse(
                    response="I need to know which project to grant access to. Please specify the project code.",
                    requires_confirmation=False
                )

            result = agent.request_project_access(
                user_lan_id,
                project,
                current_user["username"]
            )
            response_text = result["message"]
            if result.get("ad_groups"):
                response_text += f" ({result['ad_groups']} AD groups)"
            action_taken = "grant_access"

        elif action == "revoke_access" and current_user["role"] in ["admin", "hr"]:
            if not user_lan_id:
                return ChatResponse(
                    response="I need to know which user to revoke access from. Please provide the LAN ID or full name.",
                    requires_confirmation=False
                )

            if not project:
                return ChatResponse(
                    response="I need to know which project to revoke access from. Please specify the project code.",
                    requires_confirmation=False
                )

            result = agent.revoke_project_access(
                user_lan_id,
                project,
                current_user["username"]
            )
            response_text = result["message"]
            if result.get("ad_groups"):
                response_text += f" ({result['ad_groups']} AD groups)"
            action_taken = "revoke_access"

        elif action == "query_access":
            if not user_lan_id and current_user["role"] in ["admin", "hr"]:
                return ChatResponse(
                    response="I need to know which user to check access for. Please provide the LAN ID or full name.",
                    requires_confirmation=False
                )

            # Use current user if no specific user provided for non-admins
            if not user_lan_id:
                user_lan_id = current_user["lan_id"]

            result = agent.get_user_access_summary(user_lan_id)
            if result["status"] == "error":
                response_text = result["message"]
            else:
                user_data = result["user"]
                projects = result["projects"]
                if projects:
                    project_list = ", ".join([f"{p['project_code']} ({p['project_name']})" for p in projects])
                    response_text = f"User {user_data['full_name']} ({user_data['lan_id']}) has access to: {project_list}"
                else:
                    response_text = f"User {user_data['full_name']} ({user_data['lan_id']}) has no active project access."
            action_taken = "query_access"

        elif action == "notify_change" and current_user["role"] == "user":
            # User notifying about project changes
            projects = nlp_processor.extract_projects_from_text(message.message)
            if projects:
                project_list = ", ".join(projects)
                response_text = f"Thank you for notifying about your project changes. I've notified the admin about your update regarding projects: {project_list}. They will review and take appropriate action."
                # Here you would typically create a notification for admin
            else:
                response_text = "I understand you want to notify about project changes. Please specify which projects you're referring to."
            action_taken = "notify_change"

        else:
            response_text = "I understand you want to manage access control. Could you please provide more specific details? For example:\n- 'Grant access to DET project for user123'\n- 'Remove user456 from OAP project'\n- 'What access does user789 have?'\n- 'I am no longer working on CART project'"

        return ChatResponse(
            response=response_text,
            action_taken=action_taken,
            user_info=user_info,
            project_info={"project": project} if project else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{lan_id}/access")
async def get_user_access(
    lan_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "hr"] and current_user["lan_id"] != lan_id:
        raise HTTPException(status_code=403, detail="Access denied")

    agent = AccessControlAgent(db)
    result = agent.get_user_access_summary(lan_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result