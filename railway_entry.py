"""
LocalLift Railway Entry Point
This specialized entry point is used for Railway deployment
It ensures proper health check initialization and startup
"""
import os
import logging
from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("railway_deployment")

# Import from main app, but with additional Railway-specific setup
from main import app as main_app

# Configure health check route explicitly for Railway
@main_app.get("/health", include_in_schema=True)
async def railway_health_check():
    """
    Health check endpoint specifically for Railway.
    Returns a simple 'ok' response that Railway's healthcheck system requires.
    """
    logger.info("Railway health check called")
    return PlainTextResponse(content="ok", status_code=200)

# Ensure CORS is properly set with all Railway-related domains
origins = os.getenv("CORS_ORIGINS", "https://locallift.vercel.app,https://locallift-production.up.railway.app").split(",")
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log startup configuration for debugging
@main_app.on_event("startup")
async def startup_event():
    logger.info("Starting LocalLift Railway deployment")
    logger.info(f"CORS Origins: {origins}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"Health Check Enabled: {os.getenv('HEALTH_CHECK_ENABLED', 'True')}")
    logger.info(f"API Host: {os.getenv('API_HOST', '0.0.0.0')}")
    logger.info(f"API Port: {os.getenv('API_PORT', os.getenv('PORT', '8000'))}")

# Export the app for Railway
app = main_app

if __name__ == "__main__":
    """
    Run the app directly if this file is executed
    """
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        "railway_entry:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
