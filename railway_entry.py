"""
Railway Deployment Entry Point

This module serves as the main entry point for Railway deployment.
It initializes all necessary components with production-specific configuration.
"""

import os
import logging
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("railway_deployment")

# Load environment variables (Railway injects these automatically)
load_dotenv()

# Import routers (similar to main.py but with production settings)
from apps.launch.router import router as launch_router
# Commented out missing modules for Railway deployment
# from apps.docs.api.version import router as docs_router
from apps.admin.routes.training_docs import router as training_docs_router
# Import other routers as needed

# Create FastAPI app with production settings
app = FastAPI(
    title="LocalLift API",
    description="API for the Local Lift platform - Production Build",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Mount static files
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Mount static directories with explicit names to avoid conflicts
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Configure CORS for production
cors_origins = os.getenv("CORS_ORIGINS", "https://locallift.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to verify the API is running in production
    """
    # Get database connection status
    from core.supabase.client import supabase_client, supabase_admin_client
    
    db_status = "connected" if supabase_client is not None else "disconnected"
    admin_db_status = "connected" if supabase_admin_client is not None else "disconnected"
    
    return {
        "status": "healthy",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "supabase_client": db_status,
        "supabase_admin_client": admin_db_status,
        "railway_project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
        "modules": {
            "gamification": os.getenv("ENABLE_GAMIFICATION", "True") == "True",
            "leaderboards": os.getenv("ENABLE_LEADERBOARDS", "True") == "True",
            "certifications": os.getenv("ENABLE_CERTIFICATIONS", "True") == "True"
        }
    }

# Include routers
app.include_router(launch_router, prefix="/api/launch")
# Commented out missing router for Railway deployment
# app.include_router(docs_router)
app.include_router(training_docs_router)
# Include other routers here as needed based on main.py

# Export app for Railway
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    # Log deployment information
    logger.info(f"Starting LocalLift on Railway deployment on port {port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"CORS Origins: {cors_origins}")
    
    # Run the application with production settings
    uvicorn.run("railway_entry:app", host="0.0.0.0", port=port, log_level="info")
