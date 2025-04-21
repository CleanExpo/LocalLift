"""
Vercel Platform Integration for LocalLift Deployment Automation
==============================================================

This module handles interactions with Vercel platform for deployment,
configuration and verification of the LocalLift frontend.
"""

import os
import json
import logging
import requests
import time

logger = logging.getLogger(__name__)

# Constants
VERCEL_API_URL = "https://api.vercel.com"
DEFAULT_TIMEOUT = 30  # seconds

class VercelAPI:
    """Vercel API client for managing deployments"""
    
    def __init__(self, token=None, team_id=None):
        """Initialize the Vercel API client
        
        Args:
            token (str, optional): Vercel API token. If not provided, will try to load from environment.
            team_id (str, optional): Vercel team ID for team projects
        """
        self.token = token or os.environ.get("VERCEL_TOKEN")
        self.team_id = team_id or os.environ.get("VERCEL_TEAM_ID")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else None
        }
    
    def _request(self, method, endpoint, params=None, data=None):
        """Make a request to Vercel API
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            data (dict, optional): Request body data
            
        Returns:
            dict: Response data
        """
        if not self.token:
            logger.error("Vercel API token not provided")
            return None
        
        # Add team_id to params if provided
        if self.team_id:
            params = params or {}
            params["teamId"] = self.team_id
        
        url = f"{VERCEL_API_URL}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Vercel API request failed: {e}")
            return None
    
    def get_projects(self):
        """Get list of projects
        
        Returns:
            list: List of project objects
        """
        response = self._request("GET", "/v9/projects")
        if not response:
            return []
        
        return response.get("projects", [])
    
    def get_project(self, project_id):
        """Get project details
        
        Args:
            project_id (str): Vercel project ID
            
        Returns:
            dict: Project details
        """
        response = self._request("GET", f"/v9/projects/{project_id}")
        return response
    
    def get_deployments(self, project_id=None, limit=5):
        """Get deployments for a project
        
        Args:
            project_id (str, optional): Vercel project ID
            limit (int, optional): Maximum number of deployments to return
            
        Returns:
            list: List of deployment objects
        """
        params = {"limit": limit}
        if project_id:
            params["projectId"] = project_id
        
        response = self._request("GET", "/v6/deployments", params=params)
        if not response:
            return []
        
        return response.get("deployments", [])
    
    def get_project_environment_variables(self, project_id):
        """Get environment variables for a project
        
        Args:
            project_id (str): Vercel project ID
            
        Returns:
            list: List of environment variable objects
        """
        response = self._request("GET", f"/v9/projects/{project_id}/env")
        if not response:
            return []
        
        return response.get("envs", [])
    
    def set_project_environment_variable(self, project_id, key, value, target=None):
        """Set an environment variable for a project
        
        Args:
            project_id (str): Vercel project ID
            key (str): Environment variable name
            value (str): Environment variable value
            target (list, optional): Deployment targets ['production', 'preview', 'development']
            
        Returns:
            bool: True if successful, False otherwise
        """
        data = {
            "key": key,
            "value": value,
            "target": target or ["production", "preview", "development"],
            "type": "plain"
        }
        
        response = self._request("POST", f"/v9/projects/{project_id}/env", data=data)
        return response is not None
    
    def trigger_deployment(self, project_id):
        """Trigger a deployment for a project
        
        Args:
            project_id (str): Vercel project ID
            
        Returns:
            dict: Deployment details or None if failed
        """
        data = {"target": "production"}
        response = self._request("POST", f"/v13/deployments", params={"projectId": project_id}, data=data)
        return response


def find_locallift_project(client):
    """Find the LocalLift project in Vercel
    
    Args:
        client (VercelAPI): Vercel API client
        
    Returns:
        str: Project ID or None if not found
    """
    projects = client.get_projects()
    
    for project in projects:
        if "locallift" in project.get("name", "").lower():
            logger.info(f"Found LocalLift project: {project['name']} ({project['id']})")
            return project["id"]
    
    logger.warning("Could not find LocalLift project in Vercel")
    return None


def update_frontend_config(project_id, client, api_endpoint):
    """Update frontend configuration to point to the correct API endpoint
    
    Args:
        project_id (str): Vercel project ID
        client (VercelAPI): Vercel API client
        api_endpoint (str): Railway API endpoint URL
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not api_endpoint:
        logger.warning("API endpoint not provided, skipping frontend config update")
        return False
    
    # Check if API_ENDPOINT environment variable exists
    env_vars = client.get_project_environment_variables(project_id)
    
    api_env_var = next((var for var in env_vars if var.get("key") == "API_ENDPOINT"), None)
    
    if api_env_var and api_env_var.get("value") == api_endpoint:
        logger.info(f"API_ENDPOINT already set to {api_endpoint}")
        return True
    
    # Set or update API_ENDPOINT environment variable
    logger.info(f"Setting API_ENDPOINT to {api_endpoint}")
    success = client.set_project_environment_variable(project_id, "API_ENDPOINT", api_endpoint)
    
    if not success:
        logger.error("Failed to set API_ENDPOINT environment variable")
        return False
    
    # Trigger a new deployment
    logger.info("Triggering deployment...")
    deployment = client.trigger_deployment(project_id)
    
    if not deployment:
        logger.error("Failed to trigger deployment")
        return False
    
    logger.info(f"Deployment triggered: {deployment.get('id')}")
    return True


def verify_vercel_deployment(endpoint_url):
    """Verify that the Vercel deployment is working
    
    Args:
        endpoint_url (str): Vercel deployment URL
        
    Returns:
        bool: True if working, False otherwise
    """
    logger.info(f"Verifying Vercel deployment at {endpoint_url}")
    
    try:
        response = requests.get(endpoint_url, timeout=DEFAULT_TIMEOUT)
        if 200 <= response.status_code < 400:
            logger.info(f"Vercel deployment is working (Status: {response.status_code})")
            return True
        else:
            logger.warning(f"Vercel deployment returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Vercel deployment: {e}")
        return False


def configure_vercel(token=None, team_id=None, api_endpoint=None, frontend_url=None):
    """Configure Vercel deployment
    
    Args:
        token (str, optional): Vercel API token
        team_id (str, optional): Vercel team ID
        api_endpoint (str, optional): Railway API endpoint to set in frontend config
        frontend_url (str, optional): Vercel frontend URL to verify
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = VercelAPI(token, team_id)
    
    if not client.token:
        logger.warning("Vercel API token not provided, skipping configuration")
        return False
    
    project_id = find_locallift_project(client)
    
    if not project_id:
        logger.error("Could not find LocalLift project in Vercel")
        return False
    
    # Update frontend configuration if API endpoint is provided
    if api_endpoint:
        logger.info(f"Updating frontend config to use API endpoint: {api_endpoint}")
        config_updated = update_frontend_config(project_id, client, api_endpoint)
        
        if not config_updated:
            logger.error("Failed to update frontend configuration")
            return False
        
        # Wait for deployment to complete
        logger.info("Waiting for deployment to complete...")
        time.sleep(30)
    
    # Verify deployment
    if frontend_url:
        return verify_vercel_deployment(frontend_url)
    
    return True
