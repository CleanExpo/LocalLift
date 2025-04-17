"""
Railway entry point for the LocalLift backend

This is the main entry point for the Railway deployment of the LocalLift application.
It configures the FastAPI app and adds the necessary middleware and routes for deployment.
"""
import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import the main application
from main import app as main_app

# Create a new app specifically for Railway deployment
app = FastAPI(
    title="LocalLift API",
    description="LocalLift backend API for supporting local businesses",
    version="1.0.0",
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "https://local-lift-*.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for Railway
    """
    return {"status": "healthy", "environment": "railway"}

# Include all routes from the main application
app.include_router(main_app.router)

# Add error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Log the error
        print(f"Error processing request: {e}")
        # Return a JSON response
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"},
        )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request
    print(f"Request: {request.method} {request.url.path}")
    
    # Process the request
    response = await call_next(request)
    
    # Log the response
    print(f"Response: {response.status_code}")
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("railway_entry:app", host="0.0.0.0", port=port, reload=False)
