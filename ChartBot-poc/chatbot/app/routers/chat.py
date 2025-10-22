from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..schemas import ChatMessage, ChatResponse
from ..agents.nlp_processor import NLPProcessor
from ..agents.access_agent import AccessControlAgent

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
        
        # Handle different actions
        if nlp_result["action"] == "onboard_user":
            # Extract projects from message
            projects = extract_projects_from_message(message.message)
            result = agent.onboard_user_to_projects(
                nlp_result["user_lan_id"],
                extract_full_name(message.message),
                projects,
                current_user["username"]
            )
            response_text = f"User onboarded: {result}"
            action_taken = "onboard"
            
        elif nlp_result["action"] == "grant_access":
            result = agent.request_project_access(
                nlp_result["user_lan_id"],
                nlp_result["project"],
                current_user["username"]
            )
            response_text = result["message"]
            action_taken = "grant_access"
            
        elif nlp_result["action"] == "revoke_access":
            result = agent.revoke_project_access(
                nlp_result["user_lan_id"],
                nlp_result["project"],
                current_user["username"]
            )
            response_text = result["message"]
            action_taken = "revoke_access"
            
        else:
            response_text = "I understand you want to manage access. Could you provide more specific details?"
        
        return ChatResponse(
            response=response_text,
            action_taken=action_taken
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_projects_from_message(message: str) -> List[str]:
    projects = ["det", "cart", "oap", "pmba", "eo"]
    found_projects = []
    for project in projects:
        if project in message.lower():
            found_projects.append(project)
    return found_projects

def extract_full_name(message: str) -> str:
    # Simple extraction - in real implementation use better NLP
    words = message.split()
    if len(words) >= 2:
        return " ".join(words[:2])  # Assume first two words are name
    return "Unknown User"