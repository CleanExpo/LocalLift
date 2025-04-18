"""
Admin API router for Local Lift application.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.router import get_current_active_user
from core.auth.schemas import UserRead, UserCreate, UserUpdate
from core.database.connection import get_db

router = APIRouter()


# User Management
@router.get("/users", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    region_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        role: Filter by user role
        region_id: Filter by region_id
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[UserRead]: List of users
    """
    from core.supabase.client import get_supabase_admin_client
    
    # Check admin permissions
    if current_user.role != "admin" and current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and managers can list users"
        )
    
    try:
        # Get admin client to access all users
        supabase_admin = get_supabase_admin_client()
        
        # Fetch users from Supabase
        response = supabase_admin.auth.admin.list_users()
        supabase_users = response.users if response and hasattr(response, 'users') else []
        
        # Convert Supabase users to UserRead objects
        users = []
        for su in supabase_users:
            # Get app_metadata and metadata for each user
            app_metadata = su.app_metadata or {}
            user_metadata = su.user_metadata or {}
            
            # Extract role and region_id from app_metadata
            user_role = app_metadata.get("role", "client")
            user_region_id = app_metadata.get("region_id")
            
            # Apply role filter if provided
            if role and user_role != role:
                continue
                
            # Apply region_id filter if provided
            if region_id and user_region_id != region_id:
                continue
                
            # Create UserRead object from Supabase user data
            user = UserRead(
                id=su.id,
                email=su.email,
                name=user_metadata.get("full_name", su.email),
                role=user_role,
                region_id=user_region_id,
                permissions=app_metadata.get("permissions", []),
                is_active=not su.banned
            )
            users.append(user)
        
        # Apply pagination
        return users[skip:min(skip+limit, len(users))]
        
    except Exception as e:
        import logging
        logging.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only).
    
    Args:
        user: User data for creation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserRead: The newly created user
    """
    from core.supabase.client import get_supabase_admin_client
    
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users"
        )
    
    try:
        # Get admin client
        supabase_admin = get_supabase_admin_client()
        
        # Setup user metadata
        user_metadata = {
            "full_name": user.name
        }
        
        # Setup app_metadata for role-based access control
        app_metadata = {
            "role": user.role,
            "region_id": user.region_id if user.region_id else None
        }
        
        # Set default permissions based on role
        permissions = []
        if user.role == "admin":
            permissions = ["admin:all"]
        elif user.role == "manager":
            permissions = ["read:users", "create:client", "update:client", "read:reports"]
        elif user.role == "client":
            permissions = ["read:profile", "update:profile"]
        
        app_metadata["permissions"] = permissions
        
        # Create user with Supabase
        response = supabase_admin.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": user_metadata,
            "app_metadata": app_metadata
        })
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
            
        supabase_user = response.user
        
        # Return the created user
        return UserRead(
            id=supabase_user.id,
            email=supabase_user.email,
            name=user.name,
            role=user.role,
            region_id=user.region_id,
            permissions=permissions,
            is_active=True
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error creating user: {str(e)}")
        
        # Handle duplicate email error
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(
    user_id: str,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    
    Args:
        user_id: The user UUID to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserRead: The requested user
    """
    from core.supabase.client import get_supabase_admin_client
    
    # Check permissions (admin, manager, or own profile)
    if current_user.role != "admin" and current_user.role != "manager" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile or you need admin/manager permissions"
        )
    
    try:
        # Get admin client
        supabase_admin = get_supabase_admin_client()
        
        # Get user by ID
        response = supabase_admin.auth.admin.get_user_by_id(user_id)
        
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        supabase_user = response.user
        
        # Extract metadata
        app_metadata = supabase_user.app_metadata or {}
        user_metadata = supabase_user.user_metadata or {}
        
        # Create user object
        user = UserRead(
            id=supabase_user.id,
            email=supabase_user.email,
            name=user_metadata.get("full_name", supabase_user.email),
            role=app_metadata.get("role", "client"),
            region_id=app_metadata.get("region_id"),
            permissions=app_metadata.get("permissions", []),
            is_active=not supabase_user.banned
        )
        
        return user
        
    except Exception as e:
        import logging
        logging.error(f"Error retrieving user: {str(e)}")
        
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user.
    
    Args:
        user_id: The user UUID to update
        user_update: Updated user data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserRead: The updated user
    """
    from core.supabase.client import get_supabase_admin_client
    
    # Check permissions
    is_admin = current_user.role == "admin"
    is_manager = current_user.role == "manager"
    is_self = str(current_user.id) == user_id
    
    # Only admins can update roles
    if not is_admin and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change roles"
        )
    
    # Regular users can only update their own profile
    if not (is_admin or is_manager) and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Managers can only update client users
    if is_manager and not is_self:
        # Need to check if target user is a client
        try:
            # Get the target user first to check their role
            supabase_admin = get_supabase_admin_client()
            user_response = supabase_admin.auth.admin.get_user_by_id(user_id)
            
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
            target_user = user_response.user
            app_metadata = target_user.app_metadata or {}
            target_role = app_metadata.get("role", "client")
            
            if target_role != "client":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Managers can only update client users"
                )
        except Exception as e:
            import logging
            logging.error(f"Error checking user role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking user role: {str(e)}"
            )
    
    try:
        # Get admin client
        supabase_admin = get_supabase_admin_client()
        
        # First get the current user data
        user_response = supabase_admin.auth.admin.get_user_by_id(user_id)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        supabase_user = user_response.user
        app_metadata = dict(supabase_user.app_metadata or {})
        user_metadata = dict(supabase_user.user_metadata or {})
        
        # Prepare update objects
        update_data = {}
        
        # Update user_metadata if name is provided
        if user_update.name:
            user_metadata["full_name"] = user_update.name
            update_data["user_metadata"] = user_metadata
        
        # Update app_metadata if role or region_id is provided
        metadata_changed = False
        
        if user_update.role is not None and is_admin:
            app_metadata["role"] = user_update.role
            metadata_changed = True
            
            # Update permissions based on new role
            permissions = []
            if user_update.role == "admin":
                permissions = ["admin:all"]
            elif user_update.role == "manager":
                permissions = ["read:users", "create:client", "update:client", "read:reports"]
            elif user_update.role == "client":
                permissions = ["read:profile", "update:profile"]
                
            app_metadata["permissions"] = permissions
        
        if user_update.region_id is not None:
            app_metadata["region_id"] = user_update.region_id
            metadata_changed = True
        
        if metadata_changed:
            update_data["app_metadata"] = app_metadata
        
        # Update email if provided
        if user_update.email:
            update_data["email"] = user_update.email
        
        # Update user with Supabase
        if update_data:
            response = supabase_admin.auth.admin.update_user_by_id(
                user_id,
                update_data
            )
            
            if not response or not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update user"
                )
                
            supabase_user = response.user
        
        # Return updated user
        return UserRead(
            id=supabase_user.id,
            email=supabase_user.email,
            name=user_metadata.get("full_name", supabase_user.email),
            role=app_metadata.get("role", "client"),
            region_id=app_metadata.get("region_id"),
            permissions=app_metadata.get("permissions", []),
            is_active=not supabase_user.banned
        )
        
    except Exception as e:
        import logging
        logging.error(f"Error updating user: {str(e)}")
        
        # Handle specific errors
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).
    
    Args:
        user_id: The user UUID to delete
        current_user: Current authenticated user
        db: Database session
    """
    from core.supabase.client import get_supabase_admin_client
    
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete users"
        )
    
    try:
        # Get admin client
        supabase_admin = get_supabase_admin_client()
        
        # Delete user with Supabase
        response = supabase_admin.auth.admin.delete_user(user_id)
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete user"
            )
        
        return None
        
    except Exception as e:
        import logging
        logging.error(f"Error deleting user: {str(e)}")
        
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


# System Configuration
@router.get("/features", response_model=dict)
async def get_features(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get system feature flags.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Feature flag status
    """
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For now, we'll return simulated feature flags from settings
    return {
        "gamification": True,
        "certifications": True,
        "gmb_integration": True,
        "reports": True
    }


@router.put("/features", response_model=dict)
async def update_features(
    features: dict,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update system feature flags.
    
    Args:
        features: Feature flag values to update
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Updated feature flag status
    """
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # This is a placeholder - in a real implementation, you would update the feature flags in the database
    
    # For now, we'll return the provided features
    return features


# System Status
@router.get("/status", response_model=dict)
async def get_system_status(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get system status information.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: System status information
    """
    # Check admin permissions
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For now, we'll return simulated system status
    return {
        "version": "0.1.0",
        "environment": "development",
        "database": "connected",
        "active_users": 42,
        "regions": 5,
        "health": "healthy"
    }
