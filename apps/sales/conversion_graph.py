"""
Sales Conversion Graph Controller Module

This module provides the controller logic for the sales conversion graph dashboard.
It processes data from the ConversionData and SalesFunnelStage models to create
visualizations that compare conversion rates between different sales reps and regions.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from core.database.session import get_db
from core.auth.dependencies import get_current_user
from apps.sales.models.conversion_data import ConversionData, DateRangeType
from apps.sales.models.sales_funnel_stage import SalesFunnelStage


class SalesConversionGraphController:
    """
    Controller for the Sales Conversion Graph dashboard widget.
    Provides data processing and visualization for sales conversion metrics.
    """

    def __init__(self, db: Session):
        """
        Initialize the controller with a database session
        
        Args:
            db: Database session
        """
        self.db = db
        
    def get_conversion_data(
        self,
        time_period: str = "monthly",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        team_id: Optional[str] = None,
        region_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get conversion data for the specified filters
        
        Args:
            time_period: Time period for data grouping
            start_date: Start date for filtering
            end_date: End date for filtering
            team_id: Team ID for filtering
            region_id: Region ID for filtering
            
        Returns:
            Dictionary with conversion data
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        
        if not start_date:
            if time_period == DateRangeType.DAILY.value:
                start_date = end_date - timedelta(days=7)
            elif time_period == DateRangeType.WEEKLY.value:
                start_date = end_date - timedelta(weeks=4)
            elif time_period == DateRangeType.MONTHLY.value:
                start_date = end_date - timedelta(days=90)
            elif time_period == DateRangeType.QUARTERLY.value:
                start_date = end_date - timedelta(days=365)
            else:  # YEARLY
                start_date = end_date - timedelta(days=730)
        
        # Build query filters
        filters = [
            ConversionData.date_range == time_period,
            ConversionData.start_date >= start_date,
            ConversionData.end_date <= end_date
        ]
        
        if team_id:
            filters.append(ConversionData.team_id == team_id)
            
        # Get conversion data
        conversion_data = self.db.query(ConversionData).filter(*filters).all()
        
        # Get team IDs from results for further processing
        team_ids = [data.team_id for data in conversion_data]
        
        # Get team information (would come from a Teams model in a real implementation)
        teams_info = self._get_teams_info(team_ids)
        
        # Get region information if region filter is applied
        region_data = {}
        if region_id:
            region_data = self._get_region_data(region_id, team_ids)
        
        # Process data for visualization
        result = {
            "time_period": time_period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "conversion_data": [data.to_dict() for data in conversion_data],
            "teams": teams_info,
            "regions": region_data,
            "summary": self._calculate_summary(conversion_data),
            "comparison": self._generate_comparison_data(conversion_data, teams_info)
        }
        
        return result
    
    def get_funnel_stages(self, conversion_data_id: str) -> List[Dict[str, Any]]:
        """
        Get funnel stages for a specific conversion data record
        
        Args:
            conversion_data_id: Conversion data ID
            
        Returns:
            List of funnel stages
        """
        stages = self.db.query(SalesFunnelStage).filter(
            SalesFunnelStage.conversion_data_id == conversion_data_id
        ).order_by(SalesFunnelStage.id).all()
        
        return [stage.to_dict() for stage in stages]
    
    def get_conversion_trends(
        self,
        team_id: Optional[str] = None,
        time_periods: int = 6,
        period_type: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Get conversion rate trends over time
        
        Args:
            team_id: Team ID for filtering
            time_periods: Number of time periods to include
            period_type: Type of time period
            
        Returns:
            Dictionary with trend data
        """
        end_date = datetime.utcnow()
        
        # Calculate start date based on period type
        if period_type == DateRangeType.DAILY.value:
            start_date = end_date - timedelta(days=time_periods)
            date_format = "%Y-%m-%d"
        elif period_type == DateRangeType.WEEKLY.value:
            start_date = end_date - timedelta(weeks=time_periods)
            date_format = "%Y-W%W"
        elif period_type == DateRangeType.MONTHLY.value:
            start_date = end_date - timedelta(days=30 * time_periods)
            date_format = "%Y-%m"
        elif period_type == DateRangeType.QUARTERLY.value:
            start_date = end_date - timedelta(days=90 * time_periods)
            date_format = "%Y-Q%q"
        else:  # YEARLY
            start_date = end_date - timedelta(days=365 * time_periods)
            date_format = "%Y"
        
        # Build query filters
        filters = [
            ConversionData.date_range == period_type,
            ConversionData.start_date >= start_date,
            ConversionData.end_date <= end_date
        ]
        
        if team_id:
            filters.append(ConversionData.team_id == team_id)
        
        # Get conversion data
        conversion_data = self.db.query(ConversionData).filter(*filters).order_by(
            ConversionData.start_date
        ).all()
        
        # Process trend data
        trends = {
            "labels": [],
            "datasets": {
                "lead_to_qualified": [],
                "qualified_to_proposal": [],
                "proposal_to_closed": [],
                "overall": []
            }
        }
        
        for data in conversion_data:
            period_label = data.start_date.strftime(date_format)
            
            if period_label not in trends["labels"]:
                trends["labels"].append(period_label)
            
            # Get rates from conversion_rates JSON
            rates = data.conversion_rates or {}
            trends["datasets"]["lead_to_qualified"].append(rates.get("lead_to_qualified", 0))
            trends["datasets"]["qualified_to_proposal"].append(rates.get("qualified_to_proposal", 0))
            trends["datasets"]["proposal_to_closed"].append(rates.get("proposal_to_closed", 0))
            trends["datasets"]["overall"].append(rates.get("lead_to_closed", 0))
        
        return trends
    
    def _get_teams_info(self, team_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get team information for the specified team IDs
        
        Args:
            team_ids: List of team IDs
            
        Returns:
            Dictionary of team information
        """
        # In a real implementation, this would query the Teams table
        # For now, we'll return mock data
        teams = {}
        for team_id in team_ids:
            teams[team_id] = {
                "id": team_id,
                "name": f"Sales Team {team_id[-4:]}",
                "region": f"Region {ord(team_id[-1]) % 5 + 1}",
                "members": 5 + (ord(team_id[-1]) % 5)
            }
        
        return teams
    
    def _get_region_data(self, region_id: str, team_ids: List[str]) -> Dict[str, Any]:
        """
        Get region data for the specified region ID
        
        Args:
            region_id: Region ID
            team_ids: List of team IDs in the region
            
        Returns:
            Dictionary with region data
        """
        # In a real implementation, this would query the Regions table
        # For now, we'll return mock data
        return {
            "id": region_id,
            "name": f"Region {region_id[-4:]}",
            "teams": len(team_ids),
            "total_reps": sum(5 + (ord(team_id[-1]) % 5) for team_id in team_ids)
        }
    
    def _calculate_summary(self, conversion_data: List[ConversionData]) -> Dict[str, Any]:
        """
        Calculate summary metrics from conversion data
        
        Args:
            conversion_data: List of ConversionData objects
            
        Returns:
            Dictionary with summary metrics
        """
        if not conversion_data:
            return {
                "average_lead_to_qualified": 0,
                "average_qualified_to_proposal": 0,
                "average_proposal_to_closed": 0,
                "average_overall": 0,
                "total_leads": 0,
                "total_qualified": 0,
                "total_proposals": 0,
                "total_closed": 0,
                "average_sale_value": 0
            }
        
        # Calculate totals
        total_leads = sum(data.lead_count for data in conversion_data)
        total_qualified = sum(data.qualified_count for data in conversion_data)
        total_proposals = sum(data.proposal_count for data in conversion_data)
        total_closed = sum(data.closed_count for data in conversion_data)
        
        # Calculate rates
        lead_to_qualified = (total_qualified / total_leads * 100) if total_leads > 0 else 0
        qualified_to_proposal = (total_proposals / total_qualified * 100) if total_qualified > 0 else 0
        proposal_to_closed = (total_closed / total_proposals * 100) if total_proposals > 0 else 0
        overall = (total_closed / total_leads * 100) if total_leads > 0 else 0
        
        # Calculate average sale value
        total_value = sum(data.average_sale_value * data.closed_count for data in conversion_data)
        average_sale_value = (total_value / total_closed) if total_closed > 0 else 0
        
        return {
            "average_lead_to_qualified": lead_to_qualified,
            "average_qualified_to_proposal": qualified_to_proposal,
            "average_proposal_to_closed": proposal_to_closed,
            "average_overall": overall,
            "total_leads": total_leads,
            "total_qualified": total_qualified,
            "total_proposals": total_proposals,
            "total_closed": total_closed,
            "average_sale_value": average_sale_value
        }
    
    def _generate_comparison_data(
        self, 
        conversion_data: List[ConversionData],
        teams_info: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comparison data between teams
        
        Args:
            conversion_data: List of ConversionData objects
            teams_info: Dictionary of team information
            
        Returns:
            Dictionary with comparison data
        """
        if not conversion_data:
            return {
                "labels": [],
                "datasets": []
            }
        
        # Group data by team
        team_data = {}
        for data in conversion_data:
            if data.team_id not in team_data:
                team_data[data.team_id] = []
            team_data[data.team_id].append(data)
        
        # Generate comparison data
        comparison = {
            "labels": ["Lead to Qualified", "Qualified to Proposal", "Proposal to Closed", "Overall"],
            "datasets": []
        }
        
        for team_id, data_list in team_data.items():
            team_name = teams_info.get(team_id, {}).get("name", f"Team {team_id[-4:]}")
            
            # Calculate team summary
            summary = self._calculate_summary(data_list)
            
            # Add dataset
            comparison["datasets"].append({
                "label": team_name,
                "data": [
                    summary["average_lead_to_qualified"],
                    summary["average_qualified_to_proposal"],
                    summary["average_proposal_to_closed"],
                    summary["average_overall"]
                ]
            })
        
        return comparison

    def generate_chart_config(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Chart.js configuration for the comparison chart
        
        Args:
            comparison_data: Comparison data from _generate_comparison_data
            
        Returns:
            Chart.js configuration object
        """
        colors = [
            "#4c78a8", "#f58518", "#e45756", "#72b7b2", 
            "#54a24b", "#eeca3b", "#b279a2", "#ff9da6"
        ]
        
        datasets = []
        for i, dataset in enumerate(comparison_data.get("datasets", [])):
            color_index = i % len(colors)
            datasets.append({
                "label": dataset["label"],
                "data": dataset["data"],
                "backgroundColor": colors[color_index] + "80",  # Add transparency
                "borderColor": colors[color_index],
                "borderWidth": 1
            })
        
        config = {
            "type": "bar",
            "data": {
                "labels": comparison_data.get("labels", []),
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "Conversion Rate (%)"
                        },
                        "ticks": {
                            "callback": "function(value) { return value + '%'; }"
                        }
                    }
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "Sales Conversion Rates by Team"
                    },
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.dataset.label + ': ' + context.raw.toFixed(1) + '%'; }"
                        }
                    }
                }
            }
        }
        
        return config


# Create API router
router = APIRouter(
    prefix="/api/sales/conversion",
    tags=["sales", "conversion"],
    responses={404: {"description": "Not found"}},
)


@router.get("/data")
async def get_conversion_data(
    time_period: str = Query("monthly", description="Time period for data"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    team_id: Optional[str] = Query(None, description="Team ID for filtering"),
    region_id: Optional[str] = Query(None, description="Region ID for filtering"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Get conversion data for visualization
    """
    # Parse dates if provided
    start_date_obj = datetime.fromisoformat(start_date) if start_date else None
    end_date_obj = datetime.fromisoformat(end_date) if end_date else None
    
    controller = SalesConversionGraphController(db)
    data = controller.get_conversion_data(
        time_period=time_period,
        start_date=start_date_obj,
        end_date=end_date_obj,
        team_id=team_id,
        region_id=region_id
    )
    
    return data


@router.get("/trends")
async def get_conversion_trends(
    team_id: Optional[str] = Query(None, description="Team ID for filtering"),
    time_periods: int = Query(6, description="Number of time periods to include"),
    period_type: str = Query("monthly", description="Type of time period"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Get conversion rate trends over time
    """
    controller = SalesConversionGraphController(db)
    trends = controller.get_conversion_trends(
        team_id=team_id,
        time_periods=time_periods,
        period_type=period_type
    )
    
    return trends


@router.get("/chart-config")
async def get_chart_config(
    time_period: str = Query("monthly", description="Time period for data"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    team_id: Optional[str] = Query(None, description="Team ID for filtering"),
    region_id: Optional[str] = Query(None, description="Region ID for filtering"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Get Chart.js configuration for the conversion graph
    """
    # Parse dates if provided
    start_date_obj = datetime.fromisoformat(start_date) if start_date else None
    end_date_obj = datetime.fromisoformat(end_date) if end_date else None
    
    controller = SalesConversionGraphController(db)
    data = controller.get_conversion_data(
        time_period=time_period,
        start_date=start_date_obj,
        end_date=end_date_obj,
        team_id=team_id,
        region_id=region_id
    )
    
    chart_config = controller.generate_chart_config(data["comparison"])
    
    return chart_config
