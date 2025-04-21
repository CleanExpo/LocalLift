"""
Main FastAPI application for LocalLift CRM Backend

This module sets up the FastAPI application with all routers, middleware,
error handling, and documentation.
"""
import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Import routers
from .auth_api import router as auth_router
from .users_api import router as users_router
from .dashboard_api import router as dashboard_router

# Create FastAPI app
app = FastAPI(
    title="LocalLift CRM API",
    description="API for LocalLift CRM platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "https://local-lift-fxu1otnh4-admin-cleanexpo247s-projects.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],  # Allow frontend and local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )

# Root route
@app.get("/")
async def root():
    """Root route that redirects to API documentation"""
    return {"message": "Welcome to LocalLift CRM API", "docs": "/api/docs"}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "version": "1.0.0"}

# Database status check
@app.get("/database/status")
async def database_status():
    """Database connection status check"""
    try:
        # This is a simple check to verify if the database connection works
        from core.database.connection import get_db_connection
        conn = get_db_connection()
        if conn:
            conn.close()  # Make sure to close the connection
            return {"status": "connected", "message": "Database connection successful"}
        else:
            return {"status": "error", "message": "Database connection failed"}
    except ImportError as ie:
        return {"status": "error", "message": f"Import error: {str(ie)}"}
    except Exception as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}

# Version info
@app.get("/api/version")
async def version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "build_date": "2025-04-19"
    }
