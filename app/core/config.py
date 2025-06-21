from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Master Database
    master_db_host: str = "localhost"
    master_db_port: int = 5432
    master_db_name: str = "master_org_db"
    master_db_user: str = "postgres"
    master_db_password: str = "postgres"
    
    # JWT
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App
    debug: bool = True
    
    @property
    def master_database_url(self) -> str:
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{self.master_db_name}"
    
    def get_org_database_url(self, org_name: str) -> str:
        org_db_name = f"org_{org_name.lower().replace(' ', '_').replace('-', '_')}"
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{org_db_name}"
    
    class Config:
        env_file = ".env"


settings = Settings()
