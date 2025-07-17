from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import structlog

from app.config import settings


logger = structlog.get_logger()
security = HTTPBearer()


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.error("Token verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        # Return user info
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            "role": payload.get("role", "user"),
            "cognito_username": payload.get("cognito:username"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "user")
        
        role_hierarchy = {
            "viewer": 1,
            "user": 2,
            "developer": 3,
            "admin": 4
        }
        
        required_level = role_hierarchy.get(required_role, 0)
        user_level = role_hierarchy.get(user_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker