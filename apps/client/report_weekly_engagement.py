"""
Weekly Engagement Report Controller

This module provides functionality to generate and display weekly engagement reports for clients.
It analyzes engagement metrics, presents trends, and provides actionable insights.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid
import json

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database.session import get_db
from core.auth.dependencies import get_current_user
from apps.client.models.engagement_record import EngagementRecord


class WeeklyEngagementReport:
    """
    Controller for generating and managing weekly engagement reports
    """
    
    def __init__(self, db: Session):
        """Initialize the report controller with database session"""
        self.db = db
    
    def generate_weekly_report(self, client_id: str, week_number: int = None, year: int = None) -> Dict[str, Any]:
        """
        Generate a weekly engagement report for the specified client
        
        Args:
            client_id: ID of the client
            week_number: Week number (1-52)
            year: Year for the report
            
        Returns:
            Dictionary containing the report data
        """
        # Default to current week if not specified
        now = datetime.now()
        if not week_number or not year:
            # Calculate the current week number and year
            year = now.year
            # ISO week calculation
            week_number = int(now.strftime("%V"))
        
        # Calculate date range for the week
        start_date, end_date = self._get_week_date_range(year, week_number)
        
        # Get metrics for the current week
        current_metrics = self._get_metrics(client_id, start_date, end_date)
        
        # Get metrics for the previous week for comparison
        prev_week_start, prev_week_end = self._get_week_date_range(
            year - 1 if week_number == 1 else year, 
            52 if week_number == 1 else week_number - 1
        )
        previous_metrics = self._get_metrics(client_id, prev_week_start, prev_week_end)
        
        # Calculate trends and changes
        trend_data = self._calculate_trends(current_metrics, previous_metrics)
        
        # Generate insights based on the data
        insights = self._generate_insights(trend_data, current_metrics, previous_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(insights, current_metrics)
        
        # Create report data
        report = {
            "client_id": client_id,
            "week_number": week_number,
            "year": year,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": current_metrics,
            "previous_metrics": previous_metrics,
            "trends": trend_data,
            "insights": insights,
            "recommendations": recommendations,
            "generated_at": now.isoformat()
        }
        
        # Save the report to the database
        self._save_report(report)
        
        return report
    
    def get_historical_reports(self, client_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get historical reports for a client
        
        Args:
            client_id: ID of the client
            limit: Maximum number of reports to return
            
        Returns:
            List of report summaries
        """
        # Query for past reports
        records = (
            self.db.query(EngagementRecord)
            .filter(EngagementRecord.client_id == client_id)
            .order_by(EngagementRecord.year.desc(), EngagementRecord.week_number.desc())
            .limit(limit)
            .all()
        )
        
        # Format into summaries
        return [
            {
                "id": record.id,
                "week_number": record.week_number,
                "year": record.year,
                "period": {
                    "start_date": record.start_date.isoformat(),
                    "end_date": record.end_date.isoformat()
                },
                "key_metrics": {
                    "views": record.metrics.get("views", 0),
                    "engagement_rate": record.metrics.get("engagement_rate", 0),
                    "conversion_rate": record.metrics.get("conversion_rate", 0)
                },
                "trends": {
                    "views": record.trends.get("views", "stable"),
                    "engagement": record.trends.get("engagement", "stable"),
                    "conversion": record.trends.get("conversion", "stable")
                },
                "generated_at": record.created_at.isoformat(),
                "viewed": record.viewed
            }
            for record in records
        ]
    
    def _get_metrics(self, client_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get engagement metrics for a specific time period
        
        Args:
            client_id: ID of the client
            start_date: Start date of the period
            end_date: End date of the period
            
        Returns:
            Dictionary of metrics
        """
        # In a real implementation, this would query actual data sources
        # For this example, we'll generate some sample metrics
        return {
            "views": self._generate_sample_metric(1000, 5000),
            "clicks": self._generate_sample_metric(50, 500),
            "calls": self._generate_sample_metric(5, 50),
            "direction_requests": self._generate_sample_metric(10, 100),
            "messages": self._generate_sample_metric(20, 200),
            "bookings": self._generate_sample_metric(2, 20),
            "engagement_rate": self._generate_sample_metric(1.0, 5.0),
            "conversion_rate": self._generate_sample_metric(0.5, 3.0),
            "average_response_time": self._generate_sample_metric(1, 24)
        }
    
    def _generate_sample_metric(self, min_value: float, max_value: float) -> float:
        """Generate a sample metric value within a range"""
        import random
        return round(random.uniform(min_value, max_value), 2)
    
    def _calculate_trends(self, current_metrics: Dict[str, Any], previous_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate trends by comparing current and previous metrics
        
        Args:
            current_metrics: Current period metrics
            previous_metrics: Previous period metrics
            
        Returns:
            Dictionary of trends and changes
        """
        trends = {}
        
        for key, current_value in current_metrics.items():
            previous_value = previous_metrics.get(key, 0)
            
            # Skip if previous value is 0 to avoid division by zero
            if previous_value == 0:
                change_pct = 100 if current_value > 0 else 0
            else:
                change_pct = ((current_value - previous_value) / previous_value) * 100
            
            # Determine trend direction
            if change_pct > 5:
                direction = "up"
            elif change_pct < -5:
                direction = "down"
            else:
                direction = "stable"
            
            trends[key] = {
                "direction": direction,
                "change_percentage": round(change_pct, 2),
                "change_value": round(current_value - previous_value, 2)
            }
        
        return trends
    
    def _generate_insights(
        self, 
        trends: Dict[str, Any], 
        current_metrics: Dict[str, Any], 
        previous_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate insights based on metrics and trends
        
        Args:
            trends: Calculated trends
            current_metrics: Current period metrics
            previous_metrics: Previous period metrics
            
        Returns:
            List of insights
        """
        insights = []
        
        # Example insights based on views trend
        views_trend = trends.get("views", {})
        if views_trend.get("direction") == "up" and views_trend.get("change_percentage", 0) > 20:
            insights.append({
                "type": "positive",
                "category": "visibility",
                "title": "Strong increase in profile views",
                "description": f"Your profile views increased by {views_trend.get('change_percentage')}% compared to last week."
            })
        elif views_trend.get("direction") == "down" and views_trend.get("change_percentage", 0) < -20:
            insights.append({
                "type": "negative",
                "category": "visibility",
                "title": "Significant drop in profile views",
                "description": f"Your profile views decreased by {abs(views_trend.get('change_percentage'))}% compared to last week."
            })
        
        # Example insight for engagement rate
        engagement_trend = trends.get("engagement_rate", {})
        if engagement_trend.get("direction") == "up":
            insights.append({
                "type": "positive",
                "category": "engagement",
                "title": "Improved customer engagement",
                "description": f"Your engagement rate increased to {current_metrics.get('engagement_rate')}%, up from {previous_metrics.get('engagement_rate')}% last week."
            })
        
        # Example insight for conversion
        conversion_trend = trends.get("conversion_rate", {})
        if conversion_trend.get("direction") == "up":
            insights.append({
                "type": "positive",
                "category": "conversion",
                "title": "Higher conversion rate",
                "description": f"Your conversion rate improved to {current_metrics.get('conversion_rate')}%, generating more business from existing traffic."
            })
        elif conversion_trend.get("direction") == "down":
            insights.append({
                "type": "negative",
                "category": "conversion",
                "title": "Declining conversion rate",
                "description": f"Your conversion rate dropped to {current_metrics.get('conversion_rate')}% from {previous_metrics.get('conversion_rate')}% last week."
            })
        
        return insights
    
    def _generate_recommendations(
        self, 
        insights: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on insights
        
        Args:
            insights: Generated insights
            metrics: Current metrics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for negative visibility insights
        if any(i["type"] == "negative" and i["category"] == "visibility" for i in insights):
            recommendations.append({
                "category": "visibility",
                "title": "Improve your online visibility",
                "description": "Schedule more posts and update your business information to increase visibility.",
                "actions": [
                    "Schedule at least 3 posts for next week",
                    "Update your business hours and information",
                    "Add recent photos of your products or services"
                ]
            })
        
        # Check engagement metrics
        if metrics.get("engagement_rate", 0) < 3.0:
            recommendations.append({
                "category": "engagement",
                "title": "Boost customer engagement",
                "description": "Encourage more interactions with your online presence.",
                "actions": [
                    "Respond to all customer questions within 2 hours",
                    "Create interactive posts that ask questions",
                    "Run a limited-time promotion to drive engagement"
                ]
            })
        
        # Check response time
        if metrics.get("average_response_time", 0) > 5:
            recommendations.append({
                "category": "responsiveness",
                "title": "Improve response time",
                "description": f"Your average response time of {metrics.get('average_response_time')} hours is too high. Aim to respond faster.",
                "actions": [
                    "Set up notifications for new messages",
                    "Create saved responses for common questions",
                    "Delegate response duties during busy hours"
                ]
            })
        
        return recommendations
    
    def _get_week_date_range(self, year: int, week_number: int) -> Tuple[datetime, datetime]:
        """
        Get the date range for a specific week number
        
        Args:
            year: Year
            week_number: Week number (1-52)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        import datetime as dt
        from datetime import timedelta
        
        # Find the first day of the year
        first_day = dt.datetime(year, 1, 1)
        
        # Find the first day of the week (the ISO standard considers Monday as the first day)
        first_day_of_week = first_day + timedelta(days=((8 - first_day.isoweekday()) % 7))
        
        # Adjust to the correct week
        start_date = first_day_of_week + timedelta(weeks=week_number - 1)
        
        # End date is 7 days later
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return start_date, end_date
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """
        Save the report to the database
        
        Args:
            report: The generated report
        """
        # Create a new record
        start_date = datetime.fromisoformat(report["period"]["start_date"])
        end_date = datetime.fromisoformat(report["period"]["end_date"])
        
        record = EngagementRecord(
            id=str(uuid.uuid4()),
            client_id=report["client_id"],
            week_number=report["week_number"],
            year=report["year"],
            start_date=start_date,
            end_date=end_date,
            metrics=report["metrics"],
            trends=report["trends"],
            insights=[{
                "type": insight["type"],
                "category": insight["category"],
                "title": insight["title"],
                "description": insight["description"]
            } for insight in report["insights"]],
            recommendations=[{
                "category": rec["category"],
                "title": rec["title"],
                "description": rec["description"],
                "actions": rec["actions"]
            } for rec in report["recommendations"]],
            viewed=False,
            created_at=datetime.now()
        )
        
        self.db.add(record)
        self.db.commit()
        
    def mark_report_viewed(self, report_id: str) -> bool:
        """
        Mark a report as viewed
        
        Args:
            report_id: ID of the report
            
        Returns:
            True if the report was marked as viewed, False otherwise
        """
        record = self.db.query(EngagementRecord).filter(EngagementRecord.id == report_id).first()
        
        if not record:
            return False
            
        record.viewed = True
        record.viewed_at = datetime.now()
        
        self.db.commit()
        return True


# Factory function to create a report controller
def get_report_controller(db: Session = Depends(get_db)):
    """Factory function to create a WeeklyEngagementReport instance"""
    return WeeklyEngagementReport(db)
