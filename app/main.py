import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import Base, master_engine
from .api.v1 import organization, auth


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables in master database
Base.metadata.create_all(bind=master_engine)

app = FastAPI(
    title="Organization Management API",
    description="A comprehensive API for managing organizations with dynamic database creation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(organization.router, prefix="/org", tags=["organizations"])
app.include_router(auth.router, prefix="/admin", tags=["authentication"])


@app.get("/")
def root():
    return {"message": "Organization Management API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
