from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Database Configuration
master_engine = create_engine(settings.master_database_url)
MasterSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=master_engine)
Base = declarative_base()


def get_master_db():
    db = MasterSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_organization_database(org_name: str) -> str:
    """Create a new database for the organization and return its connection string"""
    org_db_name = f"org_{org_name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Create database using master connection
    master_conn = master_engine.connect()
    master_conn = master_conn.execution_options(autocommit=True)
    
    try:
        # Check if database already exists
        result = master_conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": org_db_name}
        )
        
        if result.fetchone() is None:
            # Create the database
            master_conn.execute(text(f'CREATE DATABASE "{org_db_name}"'))
            logger.info(f"Created database: {org_db_name}")
        else:
            logger.info(f"Database already exists: {org_db_name}")
            
    except Exception as e:
        logger.error(f"Error creating database {org_db_name}: {e}")
        raise
    finally:
        master_conn.close()
    
    # Create tables in the new database
    org_db_url = settings.get_org_database_url(org_name)
    org_engine = create_engine(org_db_url)
    
    # Import and create all tables
    from ..models.user import User
    Base.metadata.create_all(bind=org_engine)
    
    return org_db_url


def get_organization_db(org_name: str):
    """Get database session for specific organization"""
    org_db_url = settings.get_org_database_url(org_name)
    org_engine = create_engine(org_db_url)
    OrgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=org_engine)
    
    db = OrgSessionLocal()
    try:
        yield db
    finally:
        db.close()
