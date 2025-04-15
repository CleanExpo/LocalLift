"""
LocalLift Web Application
"""
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core.config import get_settings
from core.database.connection import get_db

# Initialize FastAPI app
app = FastAPI(
    title="Local Lift Web",
    description="Web interface for Local Lift platform",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
        "dashboard.html",  # You would need to create this template
        {
            "request": request,
            "data": dashboard_data
        }
    )


@app.get("/gamification", response_class=HTMLResponse)
async def gamification_page(request: Request):
    """
    Render the gamification page
    """
    # Placeholder data
    gamification_data = {
        "levels": [
            {"name": "Rookie", "min_points": 0, "max_points": 99},
            {"name": "Novice", "min_points": 100, "max_points": 249},
            {"name": "Expert", "min_points": 250, "max_points": 499}
        ],
        "achievements": [
            {"name": "First Review", "description": "Submit your first client review", "points": 10},
            {"name": "Review Master", "description": "Submit 50 client reviews", "points": 100},
            {"name": "Referral Champion", "description": "Refer 10 new clients", "points": 200}
        ]
    }
    
    return templates.TemplateResponse(
        "gamification.html",  # You would need to create this template
        {
            "request": request,
            "data": gamification_data
        }
    )


@app.get("/leaderboards", response_class=HTMLResponse)
async def leaderboards_page(request: Request):
    """
    Render the leaderboards page
    """
    # Placeholder data
    leaderboard_data = {
        "global": {
            "timeframe": "weekly",
            "entries": [
                {"rank": 1, "name": "Sarah Johnson", "region": "West", "points": 1425},
                {"rank": 2, "name": "Michael Chen", "region": "East", "points": 1380},
                {"rank": 3, "name": "Emily Rodriguez", "region": "Central", "points": 1320}
            ]
        },
        "regional": {
            # Regional leaderboard data would go here
        }
    }
    
    return templates.TemplateResponse(
        "leaderboards.html",  # You would need to create this template
        {
            "request": request,
            "data": leaderboard_data
        }
    )


@app.get("/certifications", response_class=HTMLResponse)
async def certifications_page(request: Request):
    """
    Render the certifications page
    """
    # Placeholder data
    certifications_data = {
        "categories": [
            {"id": 1, "name": "Google My Business", "description": "GMB optimization and management"},
            {"id": 2, "name": "Local SEO", "description": "Local search engine optimization techniques"},
            {"id": 3, "name": "Review Management", "description": "Managing and responding to client reviews"}
        ],
        "featured_courses": [
            {
                "id": 1, 
                "title": "GMB Optimization Fundamentals", 
                "level": 1, 
                "category_id": 1,
                "modules_count": 5,
                "duration_minutes": 120,
                "points": 50
            },
            {
                "id": 3, 
                "title": "Local SEO Best Practices", 
                "level": 2, 
                "category_id": 2,
                "modules_count": 7,
                "duration_minutes": 240,
                "points": 100
            }
        ]
    }
    
    return templates.TemplateResponse(
        "certifications.html",  # You would need to create this template
        {
            "request": request,
            "data": certifications_data
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

# Import and include API routers
from apps.client.api.badge_status import router as badge_status_router
from apps.client.api.badge_email_api import router as badge_email_router
from apps.client.api.badge_history_api import router as badge_history_router
from apps.client.api.badge_leaderboard_api import router as badge_leaderboard_router
from backend.api import router as backend_api_router
from apps.admin.badge_dashboard_admin import router as badge_admin_router

app.include_router(badge_status_router)
app.include_router(badge_email_router)
app.include_router(badge_history_router)
app.include_router(badge_leaderboard_router)
app.include_router(backend_api_router)
app.include_router(badge_admin_router)

@app.post("/api/scheduled/weekly-badge-emails")
async def trigger_weekly_badge_emails(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger weekly badge emails for all clients.
    This endpoint can be called by a scheduled job (e.g., cron)
    to send weekly badge status reports.
    """
    from apps.client.badge_weekly_emailer import send_all_weekly_reports
    
    result = await send_all_weekly_reports(background_tasks)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8002, reload=True)
