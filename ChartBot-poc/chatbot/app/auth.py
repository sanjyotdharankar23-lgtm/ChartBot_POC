from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

# Mock user database - replace with real authentication
MOCK_USERS = {
    "admin1": {"password": "admin123", "role": "admin", "lan_id": "admin1"},
    "hr1": {"password": "hr123", "role": "hr", "lan_id": "hr1"},
    "user1": {"password": "user123", "role": "user", "lan_id": "user1"}
}

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Simple token verification - replace with JWT in production
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )
    
    user_data = MOCK_USERS.get(credentials.credentials)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return {
        "username": credentials.credentials,
        "role": user_data["role"],
        "lan_id": user_data["lan_id"]
    }

get_current_user = verify_token