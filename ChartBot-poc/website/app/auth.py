from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

# Mock user database
MOCK_USERS = {
    "admin1": {"password": "admin123", "role": "admin", "lan_id": "admin1", "full_name": "System Admin"},
    "hr1": {"password": "hr123", "role": "hr", "lan_id": "hr1", "full_name": "HR Manager"},
    "sdharan1": {"password": "user123", "role": "user", "lan_id": "sdharan1", "full_name": "Sanjyot Dharankar"},
    "user1": {"password": "user123", "role": "user", "lan_id": "user1", "full_name": "Test User"}
}

security = HTTPBearer()

def verify_login(username: str, password: str):
    user_data = MOCK_USERS.get(username)
    if user_data and user_data["password"] == password:
        return {
            "username": username,
            "role": user_data["role"],
            "lan_id": user_data["lan_id"],
            "full_name": user_data["full_name"]
        }
    return None

def get_current_user(request: Request):
    # Simple cookie-based auth for demo
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_data = MOCK_USERS.get(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {
        "username": token,
        "role": user_data["role"],
        "lan_id": user_data["lan_id"],
        "full_name": user_data["full_name"]
    }