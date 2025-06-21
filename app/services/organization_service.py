from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.organization import Organization
from ..models.user import User
from ..schemas.organization import OrganizationCreate
from ..core.database import create_organization_database, Base
from app.core.security import get_password_hash
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class OrganizationService:


    @staticmethod
    def create_organization(db: Session, org_data: OrganizationCreate) -> Organization:
        """Create a new organization with dynamic database"""
        
        # Check if organization already exists
        existing_org = db.query(Organization).filter(
            Organization.name == org_data.organization_name
        ).first()
        
        if existing_org:
            raise ValueError("Organization already exists")
        
        # Create dynamic database for the organization
        org_db_url = create_organization_database(org_data.organization_name)
        
        # Create organization record in master database
        db_org = Organization(
            name=org_data.organization_name,
            admin_email=org_data.email,
            database_url=org_db_url
        )
        
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        
        # Create admin user in the organization's database
        OrganizationService._create_admin_user(org_data, org_db_url)
        
        logger.info(f"Created organization: {org_data.organization_name}")
        return db_org


    @staticmethod
    def _create_admin_user(org_data: OrganizationCreate, org_db_url: str):
        """Create admin user in organization's database"""
        org_engine = create_engine(org_db_url)
        OrgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=org_engine)
        
        org_db = OrgSessionLocal()
        try:
            # Create admin user
            hashed_password = get_password_hash(org_data.password)
            admin_user = User(
                email=org_data.email,
                hashed_password=hashed_password,
                is_admin=True,
                is_active=True
            )
            
            org_db.add(admin_user)
            org_db.commit()
            logger.info(f"Created admin user for organization: {org_data.organization_name}")
            
        finally:
            org_db.close()


    @staticmethod
    def get_organization_by_name(db: Session, org_name: str) -> Organization:
        """Get organization by name"""
        return db.query(Organization).filter(Organization.name == org_name).first()
