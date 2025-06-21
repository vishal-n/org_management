from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import psycopg2
from .config import settings

logger = logging.getLogger(__name__)

# Master Database Configuration
master_engine = create_engine(settings.master_database_url)
MasterSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=master_engine
)
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
    
    # Use psycopg2 directly to create database (avoids transaction issues)
    try:
        # Connect to PostgreSQL server (not a specific database)
        conn = psycopg2.connect(
            host=settings.master_db_host,
            port=settings.master_db_port,
            user=settings.master_db_user,
            password=settings.master_db_password,
            database='postgres'  # Connect to default postgres database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (org_db_name,)
        )
        
        if cursor.fetchone() is None:
            # Create the database
            cursor.execute(f'CREATE DATABASE "{org_db_name}"')
            logger.info(f"Created database: {org_db_name}")
        else:
            logger.info(f"Database already exists: {org_db_name}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database {org_db_name}: {e}")
        raise
    
    # Create tables in the new database
    org_db_url = settings.get_org_database_url(org_name)
    org_engine = create_engine(org_db_url)
    
    # Import and create all tables
    from ..models.user import User  # noqa: F401
    Base.metadata.create_all(bind=org_engine)
    
    return org_db_url


def get_organization_db(org_name: str):
    """Get database session for specific organization"""
    org_db_url = settings.get_org_database_url(org_name)
    org_engine = create_engine(org_db_url)
    OrgSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=org_engine
    )
    
    db = OrgSessionLocal()
    try:
        yield db
    finally:
        db.close()
