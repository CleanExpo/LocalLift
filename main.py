"""
Local Lift - Main Application Entry Point
"""
print("--- main.py execution started ---") # Add this line for Railway logging
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import Settings, get_settings
from core.database.connection import get_db
from core.auth.router import router as auth_router
from apps.admin.router import router as admin_router
from apps.client.router import router as client_router
from apps.investor.router import router as investor_router
from apps.franchise.router import router as franchise_router
from apps.regional_manager.router import router as regional_router
from addons.gamification.router import router as gamification_router
from addons.leaderboards.router import router as leaderboards_router
from addons.certifications.router import router as certifications_router

# Initialize FastAPI app
app = FastAPI(
    title="Local Lift API",
    description="API for the Local Lift platform - Regional group CRM with gamification",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(client_router, prefix="/api/client", tags=["Client"])
app.include_router(investor_router, prefix="/api/investor", tags=["Investor"])
app.include_router(franchise_router, prefix="/api/franchise", tags=["Franchise"])
app.include_router(regional_router, prefix="/api/regional", tags=["Regional Manager"])
app.include_router(gamification_router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(leaderboards_router, prefix="/api/leaderboards", tags=["Leaderboards"])
app.include_router(certifications_router, prefix="/api/certifications", tags=["Certifications"])


@app.get("/api/health", tags=["Health"])
async def api_health_check(settings: Settings = Depends(get_settings)):
    """
    Health check endpoint to verify the API is running
    """
    return {
        "status": "healthy",
        "version": app.version,
        "environment": settings.environment,
        "features": {
            "gamification": settings.enable_gamification,
            "certifications": settings.enable_certifications
        }
    }

@app.get("/health", tags=["Health"])
async def root_health_check():
    """
    Root health check endpoint for Railway deployment
    This endpoint is used by Railway for its health checks
    """
    # Return a simple "ok" text response that's highly compatible with health check systems
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content="ok", status_code=200)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler to standardize error responses
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            }
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'

    import uvicorn

    print(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", 
        host=host, 
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
