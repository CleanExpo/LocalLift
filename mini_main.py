"""
LocalLift - Simplified Main Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Local Lift API",
    description="API for the Local Lift platform - Regional group CRM with gamification",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning basic info about the API"""
    return {
        "name": "Local Lift API",
        "version": "0.1.0",
        "status": "Running"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {
        "status": "healthy",
        "version": app.version,
        "environment": "development",
        "modules": {
            "gamification": True,
            "leaderboards": True,
            "certifications": True
        }
    }

# Gamification endpoints demo
@app.get("/api/gamification/levels", tags=["Gamification"])
async def get_levels():
    """Get gamification levels"""
    return [
        {
            "level": 1,
            "name": "Rookie",
            "min_points": 0,
            "max_points": 99
        },
        {
            "level": 2,
            "name": "Novice",
            "min_points": 100,
            "max_points": 249
        },
        {
            "level": 3,
            "name": "Expert",
            "min_points": 250,
            "max_points": 499
        }
    ]

# Leaderboard endpoints demo
@app.get("/api/leaderboards/global", tags=["Leaderboards"])
async def get_global_leaderboard():
    """Get global leaderboard"""
    return {
        "timeframe": "week",
        "entries": [
            {
                "rank": 1,
                "user_id": 105,
                "name": "Sarah Johnson",
                "points": 1425
            },
            {
                "rank": 2,
                "user_id": 108,
                "name": "Michael Chen",
                "points": 1380
            },
            {
                "rank": 3,
                "user_id": 112,
                "name": "Emily Rodriguez",
                "points": 1320
            }
        ]
    }

# Certification endpoints demo
@app.get("/api/certifications/courses", tags=["Certifications"])
async def get_courses():
    """Get available courses"""
    return [
        {
            "id": 1,
            "title": "GMB Optimization Fundamentals",
            "level": 1,
            "category": "gmb",
            "modules_count": 5
        },
        {
            "id": 2,
            "title": "Advanced Review Management",
            "level": 3,
            "category": "gmb",
            "modules_count": 3
        },
        {
            "id": 3,
            "title": "Local SEO Best Practices",
            "level": 2,
            "category": "seo",
            "modules_count": 7
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mini_main:app", host="0.0.0.0", port=8000, reload=True)
