from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.user import User
from ..schemas.user import UserLogin
from ..core.security import verify_password, create_access_token
from ..core.config import settings
from datetime import timedelta


class AuthService:
    
    @staticmethod
    def authenticate_user(org_db_url: str, user_login: UserLogin) -> dict:
        """Authenticate user and return JWT token"""
        org_engine = create_engine(org_db_url)
        OrgSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=org_engine)
        
        org_db = OrgSessionLocal()
        try:
            # Find user in organization database
            user = org_db.query(User).filter(User.email == user_login.email).first()
            
            if not user or not verify_password(user_login.password, user.hashed_password):
                raise ValueError("Invalid credentials")
            
            if not user.is_active:
                raise ValueError("User account is inactive")
            
            # Create JWT token
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id, "is_admin": user.is_admin},
                expires_delta=access_token_expires
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "is_admin": user.is_admin
                }
            }
            
        finally:
            org_db.close()
