from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from ..core.database import get_master_db
from ..core.security import verify_token


security = HTTPBearer()


def get_current_user(token: str = Depends(security)):
    """Dependency to get current user from JWT token"""
    payload = verify_token(token.credentials)
    return payload
