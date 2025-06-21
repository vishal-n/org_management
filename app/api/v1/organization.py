from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_master_db
from ...schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationGet
from ...services.organization_service import OrganizationService

router = APIRouter()


@router.post("/create", response_model=OrganizationResponse)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_master_db)
):
    """Create a new organization with dynamic database"""
    try:
        organization = OrganizationService.create_organization(db, org_data)
        return organization
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization"
        )


@router.post("/get", response_model=OrganizationResponse)
def get_organization(
    org_request: OrganizationGet,
    db: Session = Depends(get_master_db)
):
    """Get organization by name"""
    organization = OrganizationService.get_organization_by_name(
        db, org_request.organization_name
    )
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization
