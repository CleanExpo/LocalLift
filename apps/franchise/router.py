"""
Franchise API router for Local Lift application.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session

from core.auth.router import get_current_active_user
from core.auth.schemas import UserRead, UserCreate, UserUpdate
from core.database.connection import get_db

router = APIRouter()


# Franchise Management
@router.get("/info", response_model=dict)
async def get_franchise_info(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the current franchise.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Franchise information
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch franchise data from the database
    
    # For now, we'll simulate franchise data
    franchise = {
        "id": 1,
        "name": "San Francisco Metro",
        "region_id": 1,
        "region_name": "West Coast",
        "address": "123 Market St, San Francisco, CA 94105",
        "contact_email": "sf.metro@locallift.com",
        "contact_phone": "555-123-4567",
        "established_date": "2024-01-15",
        "service_area": "San Francisco Bay Area",
        "status": "active",
        "owner": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        },
        "performance_index": 92,
        "clients_count": 25
    }
    
    return franchise


# Client Management
@router.get("/clients", response_model=List[dict])
async def get_franchise_clients(
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get clients managed by this franchise.
    
    Args:
        status: Filter by client status (active, inactive, pending)
        search: Search by client name or email
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of clients
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch clients from the database
    
    # For now, we'll simulate clients data
    clients = [
        {
            "id": 101,
            "name": "Acme Corporation",
            "email": "contact@acme.com",
            "phone": "555-111-2222",
            "address": "789 Oak St, San Francisco, CA 94103",
            "business_type": "Retail",
            "join_date": "2024-01-20",
            "status": "active",
            "gmb_linked": True,
            "points": 250,
            "completed_tasks": 15,
            "pending_tasks": 2
        },
        {
            "id": 102,
            "name": "Bay Area Tech Solutions",
            "email": "info@bayareatech.com",
            "phone": "555-333-4444",
            "address": "456 Pine St, San Francisco, CA 94102",
            "business_type": "Technology",
            "join_date": "2024-02-10",
            "status": "active",
            "gmb_linked": True,
            "points": 180,
            "completed_tasks": 12,
            "pending_tasks": 1
        },
        {
            "id": 103,
            "name": "Golden Gate Consulting",
            "email": "hello@ggconsulting.com",
            "phone": "555-555-6666",
            "address": "123 Market St, San Francisco, CA 94105",
            "business_type": "Professional Services",
            "join_date": "2024-03-05",
            "status": "pending",
            "gmb_linked": False,
            "points": 50,
            "completed_tasks": 3,
            "pending_tasks": 5
        }
    ]
    
    # Apply status filter if provided
    if status:
        clients = [client for client in clients if client["status"] == status]
    
    # Apply search filter if provided
    if search:
        search = search.lower()
        clients = [
            client for client in clients 
            if search in client["name"].lower() or search in client["email"].lower()
        ]
    
    # Apply pagination
    return clients[skip:skip+limit]


@router.post("/clients", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: dict,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new client for this franchise.
    
    Args:
        client_data: Client data for creation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: The newly created client
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would create the client in the database
    
    # For now, we'll simulate client creation
    new_client = {
        "id": 104,
        "name": client_data.get("name", "New Client"),
        "email": client_data.get("email", "client@example.com"),
        "phone": client_data.get("phone", "555-123-4567"),
        "address": client_data.get("address", "123 Example St, San Francisco, CA"),
        "business_type": client_data.get("business_type", "Other"),
        "join_date": "2025-04-14",
        "status": "pending",
        "gmb_linked": False,
        "points": 0,
        "completed_tasks": 0,
        "pending_tasks": 0,
        "message": "Client created successfully"
    }
    
    return new_client


@router.get("/clients/{client_id}", response_model=dict)
async def get_client(
    client_id: int = Path(..., ge=1),
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific client.
    
    Args:
        client_id: The ID of the client
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Detailed client information
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch the client from the database
    
    # For now, we'll simulate client data
    clients = {
        101: {
            "id": 101,
            "name": "Acme Corporation",
            "email": "contact@acme.com",
            "phone": "555-111-2222",
            "address": "789 Oak St, San Francisco, CA 94103",
            "business_type": "Retail",
            "join_date": "2024-01-20",
            "status": "active",
            "gmb_linked": True,
            "gmb_details": {
                "listing_url": "https://g.page/acme-corporation",
                "rating": 4.7,
                "reviews_count": 35,
                "categories": ["Retail Store", "Electronics Store"]
            },
            "points": 250,
            "completed_tasks": 15,
            "pending_tasks": 2,
            "recent_activities": [
                {
                    "date": "2025-04-10",
                    "activity": "Completed GMB task: Respond to reviews",
                    "points": 10
                },
                {
                    "date": "2025-04-05",
                    "activity": "Completed course: GMB Optimization Fundamentals",
                    "points": 50
                }
            ],
            "courses": [
                {
                    "id": 1,
                    "title": "GMB Optimization Fundamentals",
                    "status": "completed",
                    "completion_date": "2025-04-05"
                }
            ],
            "contact_person": "John Smith",
            "contact_role": "Marketing Manager"
        },
        102: {
            "id": 102,
            "name": "Bay Area Tech Solutions",
            "email": "info@bayareatech.com",
            "phone": "555-333-4444",
            "address": "456 Pine St, San Francisco, CA 94102",
            "business_type": "Technology",
            "join_date": "2024-02-10",
            "status": "active",
            "gmb_linked": True,
            "gmb_details": {
                "listing_url": "https://g.page/bay-area-tech",
                "rating": 4.5,
                "reviews_count": 28,
                "categories": ["IT Services", "Software Company"]
            },
            "points": 180,
            "completed_tasks": 12,
            "pending_tasks": 1,
            "recent_activities": [
                {
                    "date": "2025-04-12",
                    "activity": "Completed GMB task: Update business hours",
                    "points": 5
                }
            ],
            "courses": [
                {
                    "id": 1,
                    "title": "GMB Optimization Fundamentals",
                    "status": "in_progress",
                    "progress": 60
                }
            ],
            "contact_person": "Emily Chen",
            "contact_role": "CEO"
        },
        103: {
            "id": 103,
            "name": "Golden Gate Consulting",
            "email": "hello@ggconsulting.com",
            "phone": "555-555-6666",
            "address": "123 Market St, San Francisco, CA 94105",
            "business_type": "Professional Services",
            "join_date": "2024-03-05",
            "status": "pending",
            "gmb_linked": False,
            "points": 50,
            "completed_tasks": 3,
            "pending_tasks": 5,
            "recent_activities": [
                {
                    "date": "2025-04-08",
                    "activity": "Account created",
                    "points": 50
                }
            ],
            "courses": [],
            "contact_person": "Robert Johnson",
            "contact_role": "Founder"
        }
    }
    
    if client_id not in clients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return clients[client_id]


# Performance Management
@router.get("/dashboard", response_model=dict)
async def get_franchise_dashboard(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get franchise dashboard data.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Dashboard data
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch dashboard data from the database
    
    # For now, we'll simulate dashboard data
    dashboard = {
        "performance": {
            "index": 92,
            "rank": 1,
            "region_rank": 1,
            "trend": "+5%",
            "clients_count": 25,
            "active_clients": 22,
            "inactive_clients": 1,
            "pending_clients": 2
        },
        "task_completion": {
            "total_tasks": 375,
            "completed_tasks": 350,
            "pending_tasks": 25,
            "completion_rate": 93.3,
            "average_completion_time": "2.3 days"
        },
        "client_engagement": {
            "average_points": 185,
            "certified_clients": 15,
            "course_enrollment_rate": 80,
            "gmb_linked_percentage": 88
        },
        "revenue": {
            "monthly": 15000,
            "quarterly": 45000,
            "yearly": 180000,
            "trend": "+12%"
        },
        "top_clients": [
            {"id": 101, "name": "Acme Corporation", "points": 250, "performance_index": 95},
            {"id": 105, "name": "Pacific Heights Realty", "points": 235, "performance_index": 92},
            {"id": 112, "name": "Marina District Dental", "points": 220, "performance_index": 90}
        ],
        "recent_activities": [
            {
                "date": "2025-04-14",
                "activity": "New client added: San Francisco Bakery",
                "client_id": 125
            },
            {
                "date": "2025-04-12",
                "activity": "Client certification: Bay Area Law Group",
                "client_id": 118
            },
            {
                "date": "2025-04-10",
                "activity": "Monthly performance report generated",
                "report_id": "2025-03"
            }
        ]
    }
    
    return dashboard


@router.get("/tasks", response_model=List[dict])
async def get_franchise_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    client_id: Optional[int] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks for the franchise.
    
    Args:
        status: Filter by task status (pending, assigned, completed, overdue)
        priority: Filter by priority (high, medium, low)
        client_id: Filter by client ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of tasks
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch tasks from the database
    
    # For now, we'll simulate tasks data
    tasks = [
        {
            "id": 1001,
            "title": "Client onboarding: San Francisco Bakery",
            "description": "Complete GMB profile setup and initial training",
            "status": "pending",
            "priority": "high",
            "client_id": 125,
            "client_name": "San Francisco Bakery",
            "assigned_to": None,
            "created_date": "2025-04-14",
            "due_date": "2025-04-21"
        },
        {
            "id": 1002,
            "title": "Quarterly review: Acme Corporation",
            "description": "Review Q1 performance and plan Q2 strategy",
            "status": "pending",
            "priority": "medium",
            "client_id": 101,
            "client_name": "Acme Corporation",
            "assigned_to": current_user.id,
            "created_date": "2025-04-10",
            "due_date": "2025-04-25"
        },
        {
            "id": 1003,
            "title": "GMB optimization: Golden Gate Consulting",
            "description": "Complete GMB verification and optimize profile",
            "status": "assigned",
            "priority": "high",
            "client_id": 103,
            "client_name": "Golden Gate Consulting",
            "assigned_to": current_user.id,
            "created_date": "2025-04-08",
            "due_date": "2025-04-18"
        },
        {
            "id": 1004,
            "title": "Follow-up training: Bay Area Tech Solutions",
            "description": "Schedule advanced GMB training session",
            "status": "completed",
            "priority": "medium",
            "client_id": 102,
            "client_name": "Bay Area Tech Solutions",
            "assigned_to": current_user.id,
            "created_date": "2025-04-01",
            "due_date": "2025-04-12",
            "completed_date": "2025-04-10"
        }
    ]
    
    # Apply status filter if provided
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Apply priority filter if provided
    if priority:
        tasks = [task for task in tasks if task["priority"] == priority]
    
    # Apply client filter if provided
    if client_id:
        tasks = [task for task in tasks if task["client_id"] == client_id]
    
    return tasks


# Reports
@router.get("/reports/performance", response_model=dict)
async def get_franchise_performance_report(
    time_period: Optional[str] = "month",
    year: Optional[int] = 2025,
    month: Optional[int] = 4,
    quarter: Optional[int] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get performance report for the franchise.
    
    Args:
        time_period: Time period for the report (month, quarter, year)
        year: Year for the report
        month: Month for the report (if time_period is month)
        quarter: Quarter for the report (if time_period is quarter)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Performance report data
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch report data from the database
    
    # For now, we'll simulate report data
    report = {
        "franchise_id": 1,
        "franchise_name": "San Francisco Metro",
        "time_period": time_period,
        "year": year,
        "month": month if time_period == "month" else None,
        "quarter": quarter if time_period == "quarter" else None,
        "overview": {
            "performance_index": 92,
            "rank_in_region": "1 of 5",
            "rank_overall": "1 of 12",
            "clients_total": 25,
            "clients_new": 3,
            "clients_lost": 0,
            "revenue": 15000,
            "revenue_change": "+12%"
        },
        "client_metrics": {
            "average_gmb_rating": 4.6,
            "reviews_total": 320,
            "reviews_new": 45,
            "reviews_responses": 42,
            "response_rate": 93.3,
            "average_response_time": "6 hours",
            "client_satisfaction": 4.8
        },
        "task_metrics": {
            "tasks_total": 125,
            "tasks_completed": 118,
            "completion_rate": 94.4,
            "average_completion_time": "2.3 days",
            "overdue_tasks": 2
        },
        "education_metrics": {
            "courses_enrolled": 18,
            "courses_completed": 15,
            "certification_rate": 60,
            "average_course_score": 92
        },
        "monthly_trend": [
            {"month": "Jan", "performance_index": 85, "revenue": 12000},
            {"month": "Feb", "performance_index": 87, "revenue": 12500},
            {"month": "Mar", "performance_index": 90, "revenue": 14000},
            {"month": "Apr", "performance_index": 92, "revenue": 15000}
        ]
    }
    
    return report


@router.get("/reports/clients", response_model=List[dict])
async def get_client_performance_report(
    status: Optional[str] = None,
    sort_by: Optional[str] = "performance",
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get client performance report for the franchise.
    
    Args:
        status: Filter by client status (active, inactive, pending)
        sort_by: Sort clients by field (performance, points, tasks, reviews)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: Client performance data
    """
    # Check if user is a franchise owner/manager
    if current_user.role != "franchise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to franchise users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch client data from the database
    
    # For now, we'll simulate client performance data
    clients = [
        {
            "id": 101,
            "name": "Acme Corporation",
            "status": "active",
            "join_date": "2024-01-20",
            "performance_index": 95,
            "points": 250,
            "tasks_completed": 15,
            "tasks_pending": 2,
            "gmb_metrics": {
                "rating": 4.7,
                "reviews": 35,
                "review_responses": 33,
                "response_rate": 94.3
            },
            "education": {
                "courses_completed": 1,
                "certifications": 1
            }
        },
        {
            "id": 102,
            "name": "Bay Area Tech Solutions",
            "status": "active",
            "join_date": "2024-02-10",
            "performance_index": 88,
            "points": 180,
            "tasks_completed": 12,
            "tasks_pending": 1,
            "gmb_metrics": {
                "rating": 4.5,
                "reviews": 28,
                "review_responses": 25,
                "response_rate": 89.3
            },
            "education": {
                "courses_completed": 0,
                "courses_in_progress": 1,
                "certifications": 0
            }
        },
        {
            "id": 105,
            "name": "Pacific Heights Realty",
            "status": "active",
            "join_date": "2024-01-25",
            "performance_index": 92,
            "points": 235,
            "tasks_completed": 18,
            "tasks_pending": 0,
            "gmb_metrics": {
                "rating": 4.8,
                "reviews": 42,
                "review_responses": 40,
                "response_rate": 95.2
            },
            "education": {
                "courses_completed": 2,
                "certifications": 1
            }
        }
    ]
    
    # Apply status filter if provided
    if status:
        clients = [client for client in clients if client["status"] == status]
    
    # Apply sorting
    if sort_by == "performance":
        clients = sorted(clients, key=lambda x: x["performance_index"], reverse=True)
    elif sort_by == "points":
        clients = sorted(clients, key=lambda x: x["points"], reverse=True)
    elif sort_by == "tasks":
        clients = sorted(clients, key=lambda x: x["tasks_completed"], reverse=True)
    elif sort_by == "reviews":
        clients = sorted(clients, key=lambda x: x["gmb_metrics"]["reviews"], reverse=True)
    
    return clients
