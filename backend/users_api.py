"""
Users API for LocalLift CRM

This module implements user management endpoints for the LocalLift CRM system,
including profile management and user preferences.
"""
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr

# Import authentication utilities
from .auth_api import get_current_user

# Import the Supabase client
from ..core.supabase.client import get_supabase_client

# Define API router
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)

# Models
class UserProfile(BaseModel):
    """User profile model"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
class UserProfileUpdate(BaseModel):
    """User profile update model - all fields optional"""
    name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    
class UserPreferences(BaseModel):
    """User preferences model"""
    theme: Optional[str] = "light"  # light or dark
    dashboard_layout: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, bool]] = None
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"
    date_format: Optional[str] = "MM/DD/YYYY"
    time_format: Optional[str] = "12h"
    
class TeamMember(BaseModel):
    """Team member model for user teams"""
    user_id: str
    name: str
    email: EmailStr
    role: str
    avatar_url: Optional[str] = None

# Routes
@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    supabase = get_supabase_client()
    
    try:
        # Get additional profile data from user_profiles table if it exists
        profile_response = supabase.table("user_profiles").select("*").eq("user_id", current_user["id"]).execute()
        
        # Start with auth user data
        profile_data = {
            "name": current_user.get("user_metadata", {}).get("name", ""),
            "email": current_user["email"],
            "avatar_url": current_user.get("user_metadata", {}).get("avatar_url", None),
        }
        
        # Add profile data if it exists
        if profile_response.data and len(profile_response.data) > 0:
            profile = profile_response.data[0]
            for key, value in profile.items():
                if key != "user_id" and key != "id" and value is not None:
                    profile_data[key] = value
        
        return UserProfile(**profile_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}",
        )
        
@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user profile"""
    supabase = get_supabase_client()
    
    try:
        user_id = current_user["id"]
        update_data = profile_update.dict(exclude_unset=True)
        
        # Update data in Supabase Auth metadata
        auth_update = {}
        if "name" in update_data:
            auth_update["name"] = update_data["name"]
        if "avatar_url" in update_data:
            auth_update["avatar_url"] = update_data["avatar_url"]
            
        if auth_update:
            supabase.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": auth_update}
            )
        
        # Get current profile data or create new profile
        profile_response = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        
        if profile_response.data and len(profile_response.data) > 0:
            # Update existing profile
            supabase.table("user_profiles").update(update_data).eq("user_id", user_id).execute()
        else:
            # Create new profile
            update_data["user_id"] = user_id
            supabase.table("user_profiles").insert(update_data).execute()
        
        # Get updated profile
        return await get_my_profile(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}",
        )

@router.get("/me/preferences", response_model=UserPreferences)
async def get_my_preferences(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user preferences"""
    supabase = get_supabase_client()
    
    try:
        # Get preferences from user_preferences table
        prefs_response = supabase.table("user_preferences").select("*").eq("user_id", current_user["id"]).execute()
        
        # Default preferences
        preferences = UserPreferences()
        
        # Update with stored preferences if they exist
        if prefs_response.data and len(prefs_response.data) > 0:
            prefs = prefs_response.data[0]
            preferences_dict = preferences.dict()
            
            for key, value in prefs.items():
                if key in preferences_dict and key != "user_id" and key != "id" and value is not None:
                    preferences_dict[key] = value
                    
            preferences = UserPreferences(**preferences_dict)
            
        return preferences
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user preferences: {str(e)}",
        )
        
@router.put("/me/preferences", response_model=UserPreferences)
async def update_my_preferences(
    preferences: UserPreferences,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user preferences"""
    supabase = get_supabase_client()
    
    try:
        user_id = current_user["id"]
        prefs_data = preferences.dict(exclude_unset=True)
        
        # Get current preferences
        prefs_response = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()
        
        if prefs_response.data and len(prefs_response.data) > 0:
            # Update existing preferences
            supabase.table("user_preferences").update(prefs_data).eq("user_id", user_id).execute()
        else:
            # Create new preferences
            prefs_data["user_id"] = user_id
            supabase.table("user_preferences").insert(prefs_data).execute()
        
        # Get updated preferences
        return await get_my_preferences(current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preferences: {str(e)}",
        )

@router.get("/me/team", response_model=List[TeamMember])
async def get_my_team(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's team (if manager or above)"""
    supabase = get_supabase_client()
    
    try:
        # Check if user is a manager or above
        role = current_user.get("role", "user")
        
        if role not in ["manager", "admin", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view team members",
            )
            
        # Get team members from user_teams table
        team_response = supabase.table("user_teams").select("user_id").eq("manager_id", current_user["id"]).execute()
        
        team_members = []
        
        if team_response.data and len(team_response.data) > 0:
            # Get information for each team member
            for member in team_response.data:
                # Get user information
                user_id = member["user_id"]
                
                # Get user data
                user_response = supabase.auth.admin.get_user_by_id(user_id)
                if user_response.user:
                    user = user_response.user
                    
                    # Get role data
                    role_response = supabase.table("user_roles").select("role").eq("user_id", user_id).execute()
                    role = "user"
                    if role_response.data and len(role_response.data) > 0:
                        role = role_response.data[0]["role"]
                        
                    # Create team member object
                    team_member = TeamMember(
                        user_id=user_id,
                        name=user.user_metadata.get("name", ""),
                        email=user.email,
                        role=role,
                        avatar_url=user.user_metadata.get("avatar_url")
                    )
                    
                    team_members.append(team_member)
            
        return team_members
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team members: {str(e)}",
        )
