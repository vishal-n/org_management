from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_master_db
from ...schemas.user import UserLogin, Token
from ...services.organization_service import OrganizationService
from ...services.auth_service import AuthService


router = APIRouter()


@router.post("/login", response_model=dict)
def admin_login(
    user_login: UserLogin,
    organization_name: str,
    db: Session = Depends(get_master_db)
):
    """Admin login endpoint"""
    # Get organization
    organization = OrganizationService.get_organization_by_name(db, organization_name)
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    try:
        # Authenticate user
        auth_result = AuthService.authenticate_user(organization.database_url, user_login)
        
        # Check if user is admin
        if not auth_result["user"]["is_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return auth_result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
