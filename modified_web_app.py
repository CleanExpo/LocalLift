"""
Modified LocalLift Web Application
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Local Lift Web",
    description="Web interface for Local Lift platform",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Settings dependency
settings = get_settings()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the homepage
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render the dashboard page
    """
    # This would normally fetch real data for the dashboard
    dashboard_data = {
        "user": {
            "name": "John Doe",
            "level": 3,
            "points": 350,
            "next_level_at": 500
        },
        "stats": {
            "reviews": 28,
            "referrals": 12,
            "completed_courses": 5
        }
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": dashboard_data
        }
    )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "version": app.version,
        "environment": settings.environment,
        "features": {
            "gamification": settings.enable_gamification,
            "leaderboards": settings.enable_leaderboards,
            "certifications": settings.enable_certifications
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("modified_web_app:app", host="0.0.0.0", port=8002, reload=True)
