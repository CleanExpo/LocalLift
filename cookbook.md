# LocalLift Cookbook

This document provides recipes and examples for common tasks in the LocalLift project.

## Table of Contents
- [Database Operations](#database-operations)
- [Authentication](#authentication)
- [Gamification](#gamification)
- [Leaderboards](#leaderboards)
- [Certifications](#certifications)
- [Frontend Development](#frontend-development)

## Database Operations

### Connecting to the Database

```python
from core.database.connection import get_db
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    # Use the db session to query the database
    items = db.query(Item).all()
    return items
```

### Using Supabase Client

```python
from core.config import get_settings
import supabase

settings = get_settings()

# Initialize Supabase client
supabase_client = supabase.create_client(
    settings.supabase_url,
    settings.supabase_key
)

# Fetch data
response = supabase_client.table("gamification.levels").select("*").execute()
levels = response.data
```

### Migrations

To run migrations:

```bash
# Reset the database and apply all migrations
npm run migrate
```

## Authentication

### User Registration

```python
@router.post("/register")
async def register_user(user_data: UserCreate):
    # Create a new user
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Store in database
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
```

### User Login

```python
@router.post("/login")
async def login(user_data: UserLogin):
    # Authenticate user
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}
```

## Gamification

### Awarding Points to a User

```python
def award_points(user_id: str, point_type_id: int, amount: int, description: str = None):
    """Award points to a user for a specific action."""
    
    user_points = UserPoints(
        user_id=user_id,
        point_type_id=point_type_id,
        amount=amount,
        description=description
    )
    
    db.add(user_points)
    db.commit()
    
    # Check if user has leveled up
    check_level_up(user_id)
    
    return user_points
```

### Granting an Achievement

```python
def grant_achievement(user_id: str, achievement_id: int):
    """Grant an achievement to a user."""
    
    # Check if user already has this achievement
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if existing:
        return existing
    
    # Award the achievement
    user_achievement = UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id
    )
    
    db.add(user_achievement)
    db.commit()
    db.refresh(user_achievement)
    
    # Get achievement details to award points
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement and achievement.points > 0:
        award_points(
            user_id=user_id,
            point_type_id=1,  # Achievement points
            amount=achievement.points,
            description=f"Achievement: {achievement.name}"
        )
    
    return user_achievement
```

## Leaderboards

### Fetching Global Leaderboard

```python
def get_global_leaderboard(timeframe: str = "weekly", limit: int = 10):
    """Get the global leaderboard for a specific timeframe."""
    
    # Get the leaderboard type for global + timeframe
    leaderboard_type = db.query(LeaderboardType).filter(
        LeaderboardType.scope == "global",
        LeaderboardType.timeframe == timeframe
    ).first()
    
    if not leaderboard_type:
        raise ValueError(f"No leaderboard type found for scope 'global' and timeframe '{timeframe}'")
    
    # Get the entries
    entries = db.query(LeaderboardEntry).filter(
        LeaderboardEntry.leaderboard_type_id == leaderboard_type.id
    ).order_by(
        LeaderboardEntry.score.desc()
    ).limit(limit).all()
    
    return entries
```

## Certifications

### Enrolling in a Course

```python
def enroll_in_course(user_id: str, course_id: int):
    """Enroll a user in a course."""
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first()
    
    if existing:
        return existing
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    # Initialize module progress for all modules in this course
    modules = db.query(Module).filter(Module.course_id == course_id).all()
    for module in modules:
        module_progress = ModuleProgress(
            enrollment_id=enrollment.id,
            module_id=module.id
        )
        db.add(module_progress)
    
    db.commit()
    
    return enrollment
```

### Marking a Module as Complete

```python
def complete_module(enrollment_id: int, module_id: int):
    """Mark a module as complete for a user."""
    
    # Get the module progress
    module_progress = db.query(ModuleProgress).filter(
        ModuleProgress.enrollment_id == enrollment_id,
        ModuleProgress.module_id == module_id
    ).first()
    
    if not module_progress:
        raise ValueError("Module progress not found")
    
    # Update progress
    module_progress.is_complete = True
    module_progress.completed_at = datetime.now()
    
    db.commit()
    db.refresh(module_progress)
    
    # Update enrollment progress
    update_enrollment_progress(enrollment_id)
    
    return module_progress
```

## Frontend Development

### Working with TailwindCSS

To build CSS files:

```bash
npm run build:css
```

To watch CSS files during development:

```bash
npm run watch:css
```

### Adding a New Template

1. Create a new HTML file in the `templates` directory
2. Extend the base template:

```html
{% extends "base.html" %}

{% block title %}Your Page Title{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```

3. Add a new route in `modified_web_app.py`:

```python
@app.get("/your-route", response_class=HTMLResponse)
async def your_route(request: Request):
    return templates.TemplateResponse(
        "your_template.html",
        {"request": request, "data": your_data}
    )
