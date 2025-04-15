"""
LocalLift API
Main application entry point for the backend API server
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="LocalLift API",
    description="Backend API for the LocalLift platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Configure templates
templates = Jinja2Templates(directory="templates")

#
# API Routes
#

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
        "environment": "development",
        "features": {
            "gamification": True,
            "leaderboards": True,
            "certifications": True
        }
    }


#
# Gamification API Routes
#

@app.get("/api/gamification/levels")
async def get_gamification_levels():
    """
    Get all gamification levels
    """
    # This would normally fetch data from the database
    levels = [
        {"level": 1, "name": "Rookie", "min_points": 0, "max_points": 99},
        {"level": 2, "name": "Novice", "min_points": 100, "max_points": 249},
        {"level": 3, "name": "Expert", "min_points": 250, "max_points": 499}
    ]
    return levels


@app.get("/api/gamification/achievements")
async def get_achievements():
    """
    Get all achievements
    """
    # This would normally fetch data from the database
    achievements = [
        {"id": 1, "name": "First Review", "description": "Submit your first client review", "points": 10},
        {"id": 2, "name": "Review Master", "description": "Submit 50 client reviews", "points": 100},
        {"id": 3, "name": "Referral Champion", "description": "Refer 10 new clients", "points": 200}
    ]
    return achievements


#
# Leaderboards API Routes
#

@app.get("/api/leaderboards/global")
async def get_global_leaderboard():
    """
    Get the global leaderboard
    """
    # This would normally fetch data from the database
    leaderboard = [
        {"rank": 1, "name": "Sarah Johnson", "region": "West", "points": 1425},
        {"rank": 2, "name": "Michael Chen", "region": "East", "points": 1380},
        {"rank": 3, "name": "Emily Rodriguez", "region": "Central", "points": 1320}
    ]
    return leaderboard


#
# Certifications API Routes
#

@app.get("/api/certifications/courses")
async def get_certification_courses():
    """
    Get all certification courses
    """
    # This would normally fetch data from the database
    courses = [
        {
            "id": 1, 
            "title": "GMB Optimization Fundamentals", 
            "category": "Google My Business",
            "level": 1, 
            "modules_count": 5,
            "duration_minutes": 120,
            "points": 50
        },
        {
            "id": 2, 
            "title": "Local SEO Best Practices", 
            "category": "Local SEO",
            "level": 2, 
            "modules_count": 7,
            "duration_minutes": 240,
            "points": 100
        }
    ]
    return courses


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8002, reload=True)
