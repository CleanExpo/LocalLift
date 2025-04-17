"""
Regional Manager API router for Local Lift application.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session

from core.auth.router import get_current_active_user
from core.auth.schemas import UserRead, UserCreate, UserUpdate
from core.database.connection import get_db

router = APIRouter()


# Region Management
@router.get("/info", response_model=dict)
async def get_region_info(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the current region.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Region information
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch region data from the database
    
    # For now, we'll simulate region data
    region = {
        "id": 1,
        "name": "West Coast",
        "location": "California, Oregon, Washington",
        "established_date": "2024-01-01",
        "status": "active",
        "manager": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        },
        "franchises_count": 5,
        "clients_count": 78,
        "performance_index": 90,
        "growth_rate": 12.5
    }
    
    return region


# Franchise Management
@router.get("/franchises", response_model=List[dict])
async def get_region_franchises(
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "performance",
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get franchises within the region.
    
    Args:
        status: Filter by franchise status (active, inactive, pending)
        search: Search by franchise name or location
        sort_by: Sort franchises by field (performance, clients, tasks)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of franchises
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch franchises from the database
    
    # For now, we'll simulate franchises data
    franchises = [
        {
            "id": 1,
            "name": "San Francisco Metro",
            "location": "San Francisco, CA",
            "contact_email": "sf.metro@locallift.com",
            "contact_phone": "555-123-4567",
            "established_date": "2024-01-15",
            "status": "active",
            "owner": {
                "id": 10,
                "name": "David Rodriguez",
                "email": "david.rodriguez@example.com"
            },
            "performance_index": 92,
            "clients_count": 25,
            "tasks_completion_rate": 94.4
        },
        {
            "id": 2,
            "name": "Los Angeles County",
            "location": "Los Angeles, CA",
            "contact_email": "la.county@locallift.com",
            "contact_phone": "555-234-5678",
            "established_date": "2024-01-20",
            "status": "active",
            "owner": {
                "id": 11,
                "name": "Maria Sanchez",
                "email": "maria.sanchez@example.com"
            },
            "performance_index": 88,
            "clients_count": 18,
            "tasks_completion_rate": 91.2
        },
        {
            "id": 3,
            "name": "Portland Area",
            "location": "Portland, OR",
            "contact_email": "portland@locallift.com",
            "contact_phone": "555-345-6789",
            "established_date": "2024-02-01",
            "status": "active",
            "owner": {
                "id": 12,
                "name": "James Wilson",
                "email": "james.wilson@example.com"
            },
            "performance_index": 85,
            "clients_count": 12,
            "tasks_completion_rate": 88.5
        },
        {
            "id": 4,
            "name": "Seattle Metro",
            "location": "Seattle, WA",
            "contact_email": "seattle@locallift.com",
            "contact_phone": "555-456-7890",
            "established_date": "2024-02-15",
            "status": "active",
            "owner": {
                "id": 13,
                "name": "Emily Johnson",
                "email": "emily.johnson@example.com"
            },
            "performance_index": 90,
            "clients_count": 15,
            "tasks_completion_rate": 92.8
        },
        {
            "id": 5,
            "name": "San Diego County",
            "location": "San Diego, CA",
            "contact_email": "sandiego@locallift.com",
            "contact_phone": "555-567-8901",
            "established_date": "2024-03-01",
            "status": "pending",
            "owner": {
                "id": 14,
                "name": "Michael Thompson",
                "email": "michael.thompson@example.com"
            },
            "performance_index": 83,
            "clients_count": 8,
            "tasks_completion_rate": 85.0
        }
    ]
    
    # Apply status filter if provided
    if status:
        franchises = [franchise for franchise in franchises if franchise["status"] == status]
    
    # Apply search filter if provided
    if search:
        search = search.lower()
        franchises = [
            franchise for franchise in franchises 
            if search in franchise["name"].lower() or search in franchise["location"].lower()
        ]
    
    # Apply sorting
    if sort_by == "performance":
        franchises = sorted(franchises, key=lambda x: x["performance_index"], reverse=True)
    elif sort_by == "clients":
        franchises = sorted(franchises, key=lambda x: x["clients_count"], reverse=True)
    elif sort_by == "tasks":
        franchises = sorted(franchises, key=lambda x: x["tasks_completion_rate"], reverse=True)
    
    return franchises


@router.get("/franchises/{franchise_id}", response_model=dict)
async def get_franchise_details(
    franchise_id: int = Path(..., ge=1),
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific franchise.
    
    Args:
        franchise_id: The ID of the franchise
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Detailed franchise information
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch franchise details from the database
    
    # For now, we'll simulate franchise details
    franchises = {
        1: {
            "id": 1,
            "name": "San Francisco Metro",
            "location": "San Francisco, CA",
            "contact_email": "sf.metro@locallift.com",
            "contact_phone": "555-123-4567",
            "address": "123 Market St, San Francisco, CA 94105",
            "established_date": "2024-01-15",
            "status": "active",
            "owner": {
                "id": 10,
                "name": "David Rodriguez",
                "email": "david.rodriguez@example.com",
                "phone": "555-987-6543"
            },
            "performance_index": 92,
            "clients_count": 25,
            "tasks_completion_rate": 94.4,
            "client_satisfaction": 4.8,
            "revenue": {
                "monthly": 15000,
                "quarterly": 45000,
                "yearly": 180000,
                "trend": "+12%"
            },
            "client_distribution": {
                "business_types": [
                    {"type": "Retail", "count": 8, "percentage": 32},
                    {"type": "Professional Services", "count": 6, "percentage": 24},
                    {"type": "Hospitality", "count": 5, "percentage": 20},
                    {"type": "Healthcare", "count": 4, "percentage": 16},
                    {"type": "Technology", "count": 2, "percentage": 8}
                ],
                "client_status": [
                    {"status": "active", "count": 22, "percentage": 88},
                    {"status": "inactive", "count": 1, "percentage": 4},
                    {"status": "pending", "count": 2, "percentage": 8}
                ]
            },
            "performance_trend": [
                {"month": "Jan", "performance_index": 85},
                {"month": "Feb", "performance_index": 87},
                {"month": "Mar", "performance_index": 90},
                {"month": "Apr", "performance_index": 92}
            ],
            "top_clients": [
                {"id": 101, "name": "Acme Corporation", "performance_index": 95},
                {"id": 105, "name": "Pacific Heights Realty", "performance_index": 92},
                {"id": 112, "name": "Marina District Dental", "performance_index": 90}
            ]
        },
        2: {
            "id": 2,
            "name": "Los Angeles County",
            "location": "Los Angeles, CA",
            "contact_email": "la.county@locallift.com",
            "contact_phone": "555-234-5678",
            "address": "456 Hollywood Blvd, Los Angeles, CA 90028",
            "established_date": "2024-01-20",
            "status": "active",
            "owner": {
                "id": 11,
                "name": "Maria Sanchez",
                "email": "maria.sanchez@example.com",
                "phone": "555-876-5432"
            },
            "performance_index": 88,
            "clients_count": 18,
            "tasks_completion_rate": 91.2,
            "client_satisfaction": 4.6,
            "revenue": {
                "monthly": 12000,
                "quarterly": 36000,
                "yearly": 144000,
                "trend": "+10%"
            },
            "client_distribution": {
                "business_types": [
                    {"type": "Entertainment", "count": 5, "percentage": 27.8},
                    {"type": "Retail", "count": 4, "percentage": 22.2},
                    {"type": "Professional Services", "count": 4, "percentage": 22.2},
                    {"type": "Healthcare", "count": 3, "percentage": 16.7},
                    {"type": "Food & Beverage", "count": 2, "percentage": 11.1}
                ],
                "client_status": [
                    {"status": "active", "count": 16, "percentage": 88.9},
                    {"status": "inactive", "count": 1, "percentage": 5.5},
                    {"status": "pending", "count": 1, "percentage": 5.6}
                ]
            },
            "performance_trend": [
                {"month": "Jan", "performance_index": 83},
                {"month": "Feb", "performance_index": 85},
                {"month": "Mar", "performance_index": 87},
                {"month": "Apr", "performance_index": 88}
            ],
            "top_clients": [
                {"id": 201, "name": "LA Entertainment Group", "performance_index": 93},
                {"id": 205, "name": "Beverly Hills Medical", "performance_index": 90},
                {"id": 212, "name": "Downtown Law Partners", "performance_index": 88}
            ]
        }
    }
    
    if franchise_id not in franchises:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Franchise not found"
        )
    
    return franchises[franchise_id]


@router.post("/franchises", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_franchise(
    franchise_data: dict,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new franchise in the region.
    
    Args:
        franchise_data: Franchise data for creation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: The newly created franchise
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would create the franchise in the database
    
    # For now, we'll simulate franchise creation
    new_franchise = {
        "id": 6,
        "name": franchise_data.get("name", "New Franchise"),
        "location": franchise_data.get("location", "New Location"),
        "contact_email": franchise_data.get("contact_email", "contact@example.com"),
        "contact_phone": franchise_data.get("contact_phone", "555-123-4567"),
        "address": franchise_data.get("address", "123 Main St, City, State 12345"),
        "established_date": "2025-04-14",
        "status": "pending",
        "owner": {
            "id": franchise_data.get("owner_id", 15),
            "name": franchise_data.get("owner_name", "New Owner"),
            "email": franchise_data.get("owner_email", "owner@example.com")
        },
        "performance_index": 0,
        "clients_count": 0,
        "tasks_completion_rate": 0,
        "message": "Franchise created successfully"
    }
    
    return new_franchise


# Performance Management
@router.get("/dashboard", response_model=dict)
async def get_region_dashboard(
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get region dashboard data.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Dashboard data
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch dashboard data from the database
    
    # For now, we'll simulate dashboard data
    dashboard = {
        "performance": {
            "index": 90,
            "rank": 1,
            "trend": "+5%",
            "franchises_count": 5,
            "active_franchises": 4,
            "pending_franchises": 1,
            "clients_count": 78,
            "active_clients": 70
        },
        "revenue": {
            "monthly": 75000,
            "quarterly": 225000,
            "yearly": 900000,
            "trend": "+12%",
            "distribution": [
                {"franchise": "San Francisco Metro", "amount": 15000, "percentage": 20},
                {"franchise": "Los Angeles County", "amount": 12000, "percentage": 16},
                {"franchise": "Portland Area", "amount": 9000, "percentage": 12},
                {"franchise": "Seattle Metro", "amount": 10500, "percentage": 14},
                {"franchise": "San Diego County", "amount": 7500, "percentage": 10},
                {"franchise": "Other", "amount": 21000, "percentage": 28}
            ]
        },
        "engagement": {
            "average_performance_index": 87.6,
            "tasks_completion_rate": 92.4,
            "client_satisfaction": 4.7,
            "gmb_linked_percentage": 93,
            "course_enrollment_rate": 78
        },
        "top_franchises": [
            {"id": 1, "name": "San Francisco Metro", "performance_index": 92, "clients": 25},
            {"id": 4, "name": "Seattle Metro", "performance_index": 90, "clients": 15},
            {"id": 2, "name": "Los Angeles County", "performance_index": 88, "clients": 18}
        ],
        "recent_activities": [
            {
                "date": "2025-04-14",
                "activity": "New franchise registration: San Diego County",
                "franchise_id": 5
            },
            {
                "date": "2025-04-12",
                "activity": "Performance milestone: San Francisco Metro reached 90+ index",
                "franchise_id": 1
            },
            {
                "date": "2025-04-10",
                "activity": "25 new clients added across region",
                "client_count": 25
            }
        ],
        "gmb_metrics": {
            "average_rating": 4.6,
            "total_reviews": 1250,
            "new_reviews_this_month": 120,
            "response_rate": 94.2
        }
    }
    
    return dashboard


# Reports
@router.get("/reports/performance", response_model=dict)
async def get_region_performance_report(
    time_period: Optional[str] = "month",
    year: Optional[int] = 2025,
    month: Optional[int] = 4,
    quarter: Optional[int] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get performance report for the region.
    
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
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch report data from the database
    
    # For now, we'll simulate report data
    report = {
        "region_id": 1,
        "region_name": "West Coast",
        "time_period": time_period,
        "year": year,
        "month": month if time_period == "month" else None,
        "quarter": quarter if time_period == "quarter" else None,
        "overview": {
            "performance_index": 90,
            "rank_overall": "1 of 3",
            "franchises_total": 5,
            "franchises_new": 1,
            "clients_total": 78,
            "clients_new": 12,
            "revenue": 75000,
            "revenue_change": "+12%"
        },
        "franchise_performance": [
            {"id": 1, "name": "San Francisco Metro", "performance_index": 92, "clients": 25, "revenue": 15000},
            {"id": 2, "name": "Los Angeles County", "performance_index": 88, "clients": 18, "revenue": 12000},
            {"id": 3, "name": "Portland Area", "performance_index": 85, "clients": 12, "revenue": 9000},
            {"id": 4, "name": "Seattle Metro", "performance_index": 90, "clients": 15, "revenue": 10500},
            {"id": 5, "name": "San Diego County", "performance_index": 83, "clients": 8, "revenue": 7500}
        ],
        "client_metrics": {
            "average_gmb_rating": 4.6,
            "reviews_total": 1250,
            "reviews_new": 120,
            "response_rate": 94.2,
            "average_response_time": "8 hours",
            "client_satisfaction": 4.7
        },
        "task_metrics": {
            "tasks_total": 625,
            "tasks_completed": 578,
            "completion_rate": 92.4,
            "average_completion_time": "2.5 days",
            "overdue_tasks": 12
        },
        "education_metrics": {
            "courses_enrolled": 95,
            "courses_completed": 68,
            "certification_rate": 72,
            "average_course_score": 88
        },
        "monthly_trend": [
            {"month": "Jan", "performance_index": 84, "revenue": 65000},
            {"month": "Feb", "performance_index": 86, "revenue": 68000},
            {"month": "Mar", "performance_index": 88, "revenue": 72000},
            {"month": "Apr", "performance_index": 90, "revenue": 75000}
        ]
    }
    
    return report


@router.get("/reports/franchises", response_model=List[dict])
async def get_franchise_comparison_report(
    status: Optional[str] = None,
    sort_by: Optional[str] = "performance",
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get franchise comparison report for the region.
    
    Args:
        status: Filter by franchise status (active, inactive, pending)
        sort_by: Sort franchises by field (performance, clients, revenue, growth)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: Franchise comparison data
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch franchise data from the database
    
    # For now, we'll simulate franchise comparison data
    franchises = [
        {
            "id": 1,
            "name": "San Francisco Metro",
            "status": "active",
            "established_date": "2024-01-15",
            "performance_index": 92,
            "clients_count": 25,
            "revenue": 15000,
            "growth_rate": 15.2,
            "task_completion_rate": 94.4,
            "client_satisfaction": 4.8,
            "gmb_metrics": {
                "average_rating": 4.7,
                "reviews": 350,
                "response_rate": 96.2
            },
            "education_metrics": {
                "courses_completed": 18,
                "certification_rate": 72
            }
        },
        {
            "id": 2,
            "name": "Los Angeles County",
            "status": "active",
            "established_date": "2024-01-20",
            "performance_index": 88,
            "clients_count": 18,
            "revenue": 12000,
            "growth_rate": 12.8,
            "task_completion_rate": 91.2,
            "client_satisfaction": 4.6,
            "gmb_metrics": {
                "average_rating": 4.5,
                "reviews": 280,
                "response_rate": 92.5
            },
            "education_metrics": {
                "courses_completed": 12,
                "certification_rate": 66.7
            }
        },
        {
            "id": 3,
            "name": "Portland Area",
            "status": "active",
            "established_date": "2024-02-01",
            "performance_index": 85,
            "clients_count": 12,
            "revenue": 9000,
            "growth_rate": 10.5,
            "task_completion_rate": 88.5,
            "client_satisfaction": 4.5,
            "gmb_metrics": {
                "average_rating": 4.4,
                "reviews": 180,
                "response_rate": 91.0
            },
            "education_metrics": {
                "courses_completed": 8,
                "certification_rate": 58.3
            }
        },
        {
            "id": 4,
            "name": "Seattle Metro",
            "status": "active",
            "established_date": "2024-02-15",
            "performance_index": 90,
            "clients_count": 15,
            "revenue": 10500,
            "growth_rate": 14.2,
            "task_completion_rate": 92.8,
            "client_satisfaction": 4.7,
            "gmb_metrics": {
                "average_rating": 4.6,
                "reviews": 210,
                "response_rate": 95.0
            },
            "education_metrics": {
                "courses_completed": 11,
                "certification_rate": 73.3
            }
        },
        {
            "id": 5,
            "name": "San Diego County",
            "status": "pending",
            "established_date": "2024-03-01",
            "performance_index": 83,
            "clients_count": 8,
            "revenue": 7500,
            "growth_rate": 8.5,
            "task_completion_rate": 85.0,
            "client_satisfaction": 4.4,
            "gmb_metrics": {
                "average_rating": 4.3,
                "reviews": 95,
                "response_rate": 90.0
            },
            "education_metrics": {
                "courses_completed": 5,
                "certification_rate": 50.0
            }
        }
    ]
    
    # Apply status filter if provided
    if status:
        franchises = [franchise for franchise in franchises if franchise["status"] == status]
    
    # Apply sorting
    if sort_by == "performance":
        franchises = sorted(franchises, key=lambda x: x["performance_index"], reverse=True)
    elif sort_by == "clients":
        franchises = sorted(franchises, key=lambda x: x["clients_count"], reverse=True)
    elif sort_by == "revenue":
        franchises = sorted(franchises, key=lambda x: x["revenue"], reverse=True)
    elif sort_by == "growth":
        franchises = sorted(franchises, key=lambda x: x["growth_rate"], reverse=True)
    
    return franchises


# Campaign Management
@router.get("/campaigns", response_model=List[dict])
async def get_region_campaigns(
    status: Optional[str] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get campaigns for the region.
    
    Args:
        status: Filter by campaign status (active, completed, planned, draft)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[dict]: List of campaigns
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would fetch campaigns from the database
    
    # For now, we'll simulate campaigns data
    campaigns = [
        {
            "id": 1,
            "name": "Spring GMB Optimization Drive",
            "description": "Region-wide push to improve GMB listings with current photos and information",
            "status": "active",
            "start_date": "2025-04-01",
            "end_date": "2025-04-30",
            "target_franchises": "all",
            "target_metrics": ["gmb_rating", "review_count", "response_rate"],
            "current_progress": 65,
            "participation_rate": 90
        },
        {
            "id": 2,
            "name": "Client Certification Program",
            "description": "Incentivize clients to complete certification courses",
            "status": "active",
            "start_date": "2025-03-15",
            "end_date": "2025-05-15",
            "target_franchises": "all",
            "target_metrics": ["course_completion", "certification_rate"],
            "current_progress": 42,
            "participation_rate": 75
        },
        {
            "id": 3,
            "name": "Summer Local SEO Boost",
            "description": "Campaign to improve local search rankings across all franchises",
            "status": "planned",
            "start_date": "2025-06-01",
            "end_date": "2025-07-31",
            "target_franchises": "all",
            "target_metrics": ["search_ranking", "website_traffic", "leads"],
            "current_progress": 0,
            "participation_rate": 0
        },
        {
            "id": 4,
            "name": "Client Referral Program",
            "description": "Encourage existing clients to refer new businesses",
            "status": "draft",
            "start_date": None,
            "end_date": None,
            "target_franchises": "active",
            "target_metrics": ["new_clients", "referral_rate"],
            "current_progress": 0,
            "participation_rate": 0
        }
    ]
    
    # Apply status filter if provided
    if status:
        campaigns = [campaign for campaign in campaigns if campaign["status"] == status]
    
    return campaigns


@router.post("/campaigns", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: dict,
    current_user: UserRead = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new campaign for the region.
    
    Args:
        campaign_data: Campaign data for creation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: The newly created campaign
    """
    # Check if user is a regional manager
    if current_user.role != "regional_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to regional manager users"
        )
    
    # This is a placeholder - in a real implementation, you would create the campaign in the database
    
    # For now, we'll simulate campaign creation
    new_campaign = {
        "id": 5,
        "name": campaign_data.get("name", "New Campaign"),
        "description": campaign_data.get("description", "Campaign description"),
        "status": "draft",
        "start_date": campaign_data.get("start_date"),
        "end_date": campaign_data.get("end_date"),
        "target_franchises": campaign_data.get("target_franchises", "all"),
        "target_metrics": campaign_data.get("target_metrics", []),
        "current_progress": 0,
        "participation_rate": 0,
        "message": "Campaign created successfully"
    }
    
    return new_campaign
