"""
Dashboard API for LocalLift CRM

This module implements dashboard data endpoints for the LocalLift CRM system,
providing summary statistics, performance metrics, engagement data, and reviews.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

# Import authentication utilities
from .auth_api import get_current_user

# Import the Supabase client
from ..core.supabase.client import get_supabase_client

# Define API router
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
    },
)

# Models
class SummaryStatistics(BaseModel):
    """Summary statistics model"""
    website_visitors: int
    inquiries: int
    review_score: float
    new_customers: int
    total_revenue: float
    compared_to_previous: Dict[str, float]  # e.g. {"website_visitors": 12.5, "inquiries": 8.3}
    
class PerformanceMetric(BaseModel):
    """Performance metric model for time-series data"""
    date: str
    value: float
    
class PerformanceData(BaseModel):
    """Performance data model"""
    metrics: Dict[str, List[PerformanceMetric]]  # e.g. {"visitors": [...], "revenue": [...]}
    insights: List[str]  # AI-generated insights about the data
    growth_rate: Dict[str, float]  # e.g. {"visitors": 5.2, "revenue": 3.7}
    
class EngagementSource(BaseModel):
    """Engagement source model"""
    source: str
    count: int
    percentage: float
    change: float  # percentage change compared to previous period
    
class EngagementData(BaseModel):
    """Engagement data model"""
    sources: List[EngagementSource]
    total: int
    most_active_day: str
    most_active_time: str
    
class Review(BaseModel):
    """Review model"""
    id: str
    platform: str
    author: str
    rating: float
    content: str
    date: str
    responded: bool
    response: Optional[str] = None
    
class ReviewsData(BaseModel):
    """Reviews data model"""
    reviews: List[Review]
    average_rating: float
    total_count: int
    rating_distribution: Dict[int, int]  # e.g. {1: 2, 2: 0, 3: 5, 4: 10, 5: 20}
    unresponded_count: int

# Helper functions
def check_analytics_permission(current_user: Dict[str, Any]):
    """Check if user has permission to view analytics"""
    role = current_user.get("role", "user")
    if role not in ["staff", "manager", "admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view analytics",
        )

def get_date_range(time_period: str) -> tuple[datetime, datetime]:
    """Get date range based on time period"""
    now = datetime.now()
    end_date = now
    
    if time_period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period == "week":
        start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_period == "quarter":
        quarter_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_period == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        # Default to month
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
    return start_date, end_date

def get_previous_period(start_date: datetime, time_period: str) -> tuple[datetime, datetime]:
    """Get previous period date range"""
    if time_period == "day":
        prev_start = start_date - timedelta(days=1)
        prev_end = start_date
    elif time_period == "week":
        prev_start = start_date - timedelta(weeks=1)
        prev_end = start_date
    elif time_period == "month":
        # Go to the first day of the previous month
        if start_date.month == 1:
            prev_start = start_date.replace(year=start_date.year - 1, month=12)
        else:
            prev_start = start_date.replace(month=start_date.month - 1)
        prev_end = start_date
    elif time_period == "quarter":
        # Go to the first day of the previous quarter
        if start_date.month <= 3:
            prev_start = start_date.replace(year=start_date.year - 1, month=10, day=1)
        else:
            prev_start = start_date.replace(month=start_date.month - 3, day=1)
        prev_end = start_date
    elif time_period == "year":
        prev_start = start_date.replace(year=start_date.year - 1)
        prev_end = start_date
    else:
        # Default to month
        if start_date.month == 1:
            prev_start = start_date.replace(year=start_date.year - 1, month=12)
        else:
            prev_start = start_date.replace(month=start_date.month - 1)
        prev_end = start_date
        
    return prev_start, prev_end

def calculate_change_percentage(current: float, previous: float) -> float:
    """Calculate percentage change"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100

# Routes
@router.get("/summary", response_model=SummaryStatistics)
async def get_summary_statistics(
    time_period: str = Query("month", description="Time period for statistics (day, week, month, quarter, year)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get summary statistics for the dashboard"""
    # Check permissions
    check_analytics_permission(current_user)
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    try:
        # Get date ranges
        start_date, end_date = get_date_range(time_period)
        prev_start, prev_end = get_previous_period(start_date, time_period)
        
        # Format dates for database queries
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        prev_start_str = prev_start.isoformat()
        prev_end_str = prev_end.isoformat()
        
        # Get website visitors
        visitors_response = supabase.table("website_visits").select("count").gt("timestamp", start_str).lt("timestamp", end_str).execute()
        prev_visitors_response = supabase.table("website_visits").select("count").gt("timestamp", prev_start_str).lt("timestamp", prev_end_str).execute()
        
        website_visitors = 0
        prev_website_visitors = 0
        
        if visitors_response.data:
            website_visitors = sum(item.get("count", 0) for item in visitors_response.data)
        
        if prev_visitors_response.data:
            prev_website_visitors = sum(item.get("count", 0) for item in prev_visitors_response.data)
            
        # Get customer inquiries
        inquiries_response = supabase.table("customer_inquiries").select("count").gt("timestamp", start_str).lt("timestamp", end_str).execute()
        prev_inquiries_response = supabase.table("customer_inquiries").select("count").gt("timestamp", prev_start_str).lt("timestamp", prev_end_str).execute()
        
        inquiries = 0
        prev_inquiries = 0
        
        if inquiries_response.data:
            inquiries = len(inquiries_response.data)
        
        if prev_inquiries_response.data:
            prev_inquiries = len(prev_inquiries_response.data)
            
        # Get review score
        reviews_response = supabase.table("customer_reviews").select("rating").gt("timestamp", start_str).lt("timestamp", end_str).execute()
        prev_reviews_response = supabase.table("customer_reviews").select("rating").gt("timestamp", prev_start_str).lt("timestamp", prev_end_str).execute()
        
        review_score = 0.0
        prev_review_score = 0.0
        
        if reviews_response.data and len(reviews_response.data) > 0:
            review_score = sum(item.get("rating", 0) for item in reviews_response.data) / len(reviews_response.data)
        
        if prev_reviews_response.data and len(prev_reviews_response.data) > 0:
            prev_review_score = sum(item.get("rating", 0) for item in prev_reviews_response.data) / len(prev_reviews_response.data)
            
        # Get new customers
        customers_response = supabase.table("customers").select("id").gt("created_at", start_str).lt("created_at", end_str).execute()
        prev_customers_response = supabase.table("customers").select("id").gt("created_at", prev_start_str).lt("created_at", prev_end_str).execute()
        
        new_customers = 0
        prev_new_customers = 0
        
        if customers_response.data:
            new_customers = len(customers_response.data)
        
        if prev_customers_response.data:
            prev_new_customers = len(prev_customers_response.data)
            
        # Get total revenue
        revenue_response = supabase.table("orders").select("amount").gt("timestamp", start_str).lt("timestamp", end_str).execute()
        prev_revenue_response = supabase.table("orders").select("amount").gt("timestamp", prev_start_str).lt("timestamp", prev_end_str).execute()
        
        total_revenue = 0.0
        prev_total_revenue = 0.0
        
        if revenue_response.data:
            total_revenue = sum(item.get("amount", 0) for item in revenue_response.data)
        
        if prev_revenue_response.data:
            prev_total_revenue = sum(item.get("amount", 0) for item in prev_revenue_response.data)
            
        # Calculate comparison percentages
        compared_to_previous = {
            "website_visitors": calculate_change_percentage(website_visitors, prev_website_visitors),
            "inquiries": calculate_change_percentage(inquiries, prev_inquiries),
            "review_score": calculate_change_percentage(review_score, prev_review_score),
            "new_customers": calculate_change_percentage(new_customers, prev_new_customers),
            "total_revenue": calculate_change_percentage(total_revenue, prev_total_revenue)
        }
        
        # Return summary statistics
        return SummaryStatistics(
            website_visitors=website_visitors,
            inquiries=inquiries,
            review_score=round(review_score, 1),
            new_customers=new_customers,
            total_revenue=round(total_revenue, 2),
            compared_to_previous=compared_to_previous
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary statistics: {str(e)}",
        )

@router.get("/performance", response_model=PerformanceData)
async def get_performance_metrics(
    time_period: str = Query("month", description="Time period for metrics (day, week, month, quarter, year)"),
    metrics: str = Query("visitors,revenue,orders", description="Comma-separated list of metrics to include"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get performance metrics for the dashboard"""
    # Check permissions
    check_analytics_permission(current_user)
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    try:
        # Get date ranges
        start_date, end_date = get_date_range(time_period)
        prev_start, prev_end = get_previous_period(start_date, time_period)
        
        # Format dates for database queries
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        prev_start_str = prev_start.isoformat()
        prev_end_str = prev_end.isoformat()
        
        # Parse requested metrics
        requested_metrics = metrics.split(",")
        
        # Initialize result structure
        metrics_data = {}
        growth_rate = {}
        
        # Get data for each requested metric
        for metric in requested_metrics:
            metric = metric.strip()
            
            if metric == "visitors":
                # Get visitors data
                visitors_response = supabase.table("website_visits").select("date,count").gt("date", start_date.date().isoformat()).lt("date", end_date.date().isoformat()).order("date").execute()
                metrics_data["visitors"] = []
                
                for item in visitors_response.data:
                    metrics_data["visitors"].append(PerformanceMetric(
                        date=item.get("date"),
                        value=item.get("count", 0)
                    ))
                    
                # Calculate growth rate
                total_current = sum(item.value for item in metrics_data["visitors"])
                
                prev_visitors_response = supabase.table("website_visits").select("count").gt("date", prev_start.date().isoformat()).lt("date", prev_end.date().isoformat()).execute()
                total_previous = sum(item.get("count", 0) for item in prev_visitors_response.data)
                
                growth_rate["visitors"] = calculate_change_percentage(total_current, total_previous)
                
            elif metric == "revenue":
                # Get revenue data
                revenue_response = supabase.table("orders").select("date,sum(amount)").gt("date", start_date.date().isoformat()).lt("date", end_date.date().isoformat()).group_by("date").order("date").execute()
                metrics_data["revenue"] = []
                
                for item in revenue_response.data:
                    metrics_data["revenue"].append(PerformanceMetric(
                        date=item.get("date"),
                        value=item.get("sum", 0)
                    ))
                    
                # Calculate growth rate
                total_current = sum(item.value for item in metrics_data["revenue"])
                
                prev_revenue_response = supabase.table("orders").select("sum(amount)").gt("date", prev_start.date().isoformat()).lt("date", prev_end.date().isoformat()).execute()
                total_previous = prev_revenue_response.data[0].get("sum", 0) if prev_revenue_response.data else 0
                
                growth_rate["revenue"] = calculate_change_percentage(total_current, total_previous)
                
            elif metric == "orders":
                # Get orders data
                orders_response = supabase.table("orders").select("date,count").gt("date", start_date.date().isoformat()).lt("date", end_date.date().isoformat()).group_by("date").order("date").execute()
                metrics_data["orders"] = []
                
                for item in orders_response.data:
                    metrics_data["orders"].append(PerformanceMetric(
                        date=item.get("date"),
                        value=item.get("count", 0)
                    ))
                    
                # Calculate growth rate
                total_current = sum(item.value for item in metrics_data["orders"])
                
                prev_orders_response = supabase.table("orders").select("count").gt("date", prev_start.date().isoformat()).lt("date", prev_end.date().isoformat()).execute()
                total_previous = len(prev_orders_response.data)
                
                growth_rate["orders"] = calculate_change_percentage(total_current, total_previous)
                
            elif metric == "reviews":
                # Get reviews data
                reviews_response = supabase.table("customer_reviews").select("date,count").gt("date", start_date.date().isoformat()).lt("date", end_date.date().isoformat()).group_by("date").order("date").execute()
                metrics_data["reviews"] = []
                
                for item in reviews_response.data:
                    metrics_data["reviews"].append(PerformanceMetric(
                        date=item.get("date"),
                        value=item.get("count", 0)
                    ))
                    
                # Calculate growth rate
                total_current = sum(item.value for item in metrics_data["reviews"])
                
                prev_reviews_response = supabase.table("customer_reviews").select("count").gt("date", prev_start.date().isoformat()).lt("date", prev_end.date().isoformat()).execute()
                total_previous = len(prev_reviews_response.data)
                
                growth_rate["reviews"] = calculate_change_percentage(total_current, total_previous)
        
        # Generate insights
        insights = []
        
        for metric, data in metrics_data.items():
            metric_growth = growth_rate.get(metric)
            
            if metric_growth > 20:
                insights.append(f"Significant growth in {metric}: +{metric_growth:.1f}% compared to previous period.")
            elif metric_growth < -20:
                insights.append(f"Notable decline in {metric}: {metric_growth:.1f}% compared to previous period.")
                
            # Find peak days
            if data:
                max_metric = max(data, key=lambda x: x.value)
                insights.append(f"Peak {metric} occurred on {max_metric.date}: {max_metric.value}")
        
        # Return performance data
        return PerformanceData(
            metrics=metrics_data,
            insights=insights,
            growth_rate=growth_rate
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}",
        )

@router.get("/engagement", response_model=EngagementData)
async def get_engagement_data(
    time_period: str = Query("month", description="Time period for engagement data (day, week, month, quarter, year)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get customer engagement data for the dashboard"""
    # Check permissions
    check_analytics_permission(current_user)
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    try:
        # Get date ranges
        start_date, end_date = get_date_range(time_period)
        prev_start, prev_end = get_previous_period(start_date, time_period)
        
        # Format dates for database queries
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        prev_start_str = prev_start.isoformat()
        prev_end_str = prev_end.isoformat()
        
        # Get engagement sources
        sources_response = supabase.table("customer_engagement").select("source,count").gt("timestamp", start_str).lt("timestamp", end_str).group_by("source").execute()
        prev_sources_response = supabase.table("customer_engagement").select("source,count").gt("timestamp", prev_start_str).lt("timestamp", prev_end_str).group_by("source").execute()
        
        # Process current period data
        current_sources = {}
        current_total = 0
        
        for item in sources_response.data:
            source = item.get("source")
            count = item.get("count", 0)
            current_sources[source] = count
            current_total += count
            
        # Process previous period data
        prev_sources = {}
        
        for item in prev_sources_response.data:
            source = item.get("source")
            count = item.get("count", 0)
            prev_sources[source] = count
            
        # Create engagement sources list
        sources_list = []
        
        for source, count in current_sources.items():
            prev_count = prev_sources.get(source, 0)
            percentage = (count / current_total * 100) if current_total > 0 else 0
            change = calculate_change_percentage(count, prev_count)
            
            sources_list.append(EngagementSource(
                source=source,
                count=count,
                percentage=round(percentage, 1),
                change=round(change, 1)
            ))
            
        # Sort by count descending
        sources_list.sort(key=lambda x: x.count, reverse=True)
        
        # Get most active day and time
        day_response = supabase.table("customer_engagement").select("day_of_week,count").gt("timestamp", start_str).lt("timestamp", end_str).group_by("day_of_week").order("count", desc=True).limit(1).execute()
        time_response = supabase.table("customer_engagement").select("hour_of_day,count").gt("timestamp", start_str).lt("timestamp", end_str).group_by("hour_of_day").order("count", desc=True).limit(1).execute()
        
        most_active_day = "Unknown"
        most_active_time = "Unknown"
        
        if day_response.data and len(day_response.data) > 0:
            day_num = day_response.data[0].get("day_of_week")
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            most_active_day = day_names[day_num - 1] if 1 <= day_num <= 7 else "Unknown"
            
        if time_response.data and len(time_response.data) > 0:
            hour = time_response.data[0].get("hour_of_day")
            if 0 <= hour <= 23:
                am_pm = "AM" if hour < 12 else "PM"
                hour_12 = hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                most_active_time = f"{hour_12} {am_pm}"
        
        # Return engagement data
        return EngagementData(
            sources=sources_list,
            total=current_total,
            most_active_day=most_active_day,
            most_active_time=most_active_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get engagement data: {str(e)}",
        )

@router.get("/reviews", response_model=ReviewsData)
async def get_reviews(
    platform: Optional[str] = Query(None, description="Filter by platform (e.g., Google, Yelp)"),
    rating: Optional[int] = Query(None, description="Filter by rating (1-5)"),
    limit: int = Query(10, description="Number of reviews to return"),
    offset: int = Query(0, description="Pagination offset"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get customer reviews for the dashboard"""
    # Check permissions - all authenticated users can see reviews
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    try:
        # Start building the query
        query = supabase.table("customer_reviews").select("*")
        
        # Apply filters
        if platform:
            query = query.eq("platform", platform)
            
        if rating:
            query = query.eq("rating", rating)
            
        # Get total count
        count_query = query
        count_response = count_query.execute()
        total_count = len(count_response.data)
        
        # Get paginated results
        query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        
        # Process reviews
        reviews_list = []
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        total_rating = 0
        unresponded_count = 0
        
        for item in count_response.data:
            # Update rating distribution
            rating = item.get("rating")
            if 1 <= rating <= 5:
                rating_distribution[rating] += 1
                total_rating += rating
                
            # Count unresponded reviews
            if not item.get("responded", False):
                unresponded_count += 1
        
        # Calculate average rating
        average_rating = (total_rating / total_count) if total_count > 0 else 0
        
        # Process paginated reviews
        for item in response.data:
            reviews_list.append(Review(
                id=item.get("id"),
                platform=item.get("platform"),
                author=item.get("author"),
                rating=item.get("rating"),
                content=item.get("content"),
                date=item.get("timestamp").split("T")[0] if item.get("timestamp") else "Unknown",
                responded=item.get("responded", False),
                response=item.get("response")
            ))
        
        # Return reviews data
        return ReviewsData(
            reviews=reviews_list,
            average_rating=round(average_rating, 1),
            total_count=total_count,
            rating_distribution=rating_distribution,
            unresponded_count=unresponded_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reviews: {str(e)}",
        )
