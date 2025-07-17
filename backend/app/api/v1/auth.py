from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
import structlog

router = APIRouter()
logger = structlog.get_logger()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login with email and password"""
    try:
        # Mock authentication - in production, use Cognito
        if (
            login_data.email == "admin@example.com"
            and login_data.password == "password"
        ):
            # Mock JWT token
            mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJuYW1lIjoiQWRtaW4gVXNlciIsInJvbGUiOiJhZG1pbiJ9.mock"

            logger.info("User logged in", email=login_data.email)

            return LoginResponse(
                access_token=mock_token,
                expires_in=1800,  # 30 minutes
                user_info={
                    "user_id": "user_123",
                    "email": "admin@example.com",
                    "name": "Admin User",
                    "role": "admin"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token"""
    try:
        # Mock token refresh - in production, use Cognito
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJuYW1lIjoiQWRtaW4gVXNlciIsInJvbGUiOiJhZG1pbiJ9.mock"
        
        return LoginResponse(
            access_token=mock_token,
            expires_in=1800,
            user_info={
                "user_id": "user_123",
                "email": "admin@example.com",
                "name": "Admin User",
                "role": "admin"
            }
        )
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout():
    """Logout (invalidate token)"""
    try:
        # In production, invalidate token in Cognito
        logger.info("User logged out")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")