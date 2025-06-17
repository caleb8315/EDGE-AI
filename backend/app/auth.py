from fastapi import HTTPException, Depends, Header
from typing import Optional
import jwt
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
import httpx
import logging

logger = logging.getLogger(__name__)

class AuthUser:
    def __init__(self, auth_id: str, email: str):
        self.auth_id = auth_id  # Supabase Auth user ID
        self.email = email

async def get_current_user(authorization: Optional[str] = Header(None)) -> AuthUser:
    """Extract and verify the current authenticated user from the Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split(" ")[1]
    
    try:
        # Verify the JWT token with Supabase
        # For now, we'll decode without verification for development
        # In production, you'd want to verify with the JWT secret
        payload = jwt.decode(token, options={"verify_signature": False})
        
        auth_id = payload.get("sub")
        email = payload.get("email")
        
        if not auth_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        return AuthUser(auth_id=auth_id, email=email)
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Optional dependency for endpoints that may or may not require auth
async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[AuthUser]:
    """Get current user if authenticated, otherwise return None."""
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None 