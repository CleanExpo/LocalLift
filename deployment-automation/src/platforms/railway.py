"""
Railway Platform Integration for LocalLift Deployment Automation
===============================================================

This module handles interactions with Railway platform for deployment,
configuration and verification of the LocalLift backend.
"""

import os
import json
import logging
import requests
import time

logger = logging.getLogger(__name__)

# Constants
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
DEFAULT_TIMEOUT = 30  # seconds

class RailwayAPI:
    """Railway API client for managing deployments"""
    
    def __init__(self, token=None):
        """Initialize the Railway API client
        
        Args:
            token (str, optional): Railway API token. If not provided, will try to load from environment.
        """
        self.token = token or os.environ.get("RAILWAY_TOKEN")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else None
        }
    
    def _request(self, query, variables=None):
        """Make a GraphQL request to Railway API
        
        Args:
            query (str): GraphQL query
            variables (dict, optional): Query variables
            
        Returns:
            dict: Response data
        """
        if not self.token:
            logger.error("Railway API token not provided")
            return None
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                RAILWAY_API_URL,
                headers=self.headers,
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Railway API request failed: {e}")
            return None
    
    def get_projects(self):
        """Get list of projects
        
        Returns:
            list: List of project objects
        """
        query = """
        query GetProjects {
            projects {
                edges {
                    node {
                        id
                        name
                        description
                        environments {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        response = self._request(query)
        if not response or "errors" in response:
            logger.error(f"Failed to get projects: {response.get('errors', 'Unknown error')}")
            return []
        
        projects = []
        for edge in response.get("data", {}).get("projects", {}).get("edges", []):
            projects.append(edge.get("node", {}))
        
        return projects
    
    def get_project_environments(self, project_id):
        """Get environments for a project
        
        Args:
            project_id (str): Railway project ID
            
        Returns:
            list: List of environment objects
        """
        query = """
        query GetEnvironments($projectId: String!) {
            project(id: $projectId) {
                environments {
                    id
                    name
                }
            }
        }
        """
        
        variables = {
            "projectId": project_id
        }
        
        response = self._request(query, variables)
        if not response or "errors" in response:
            logger.error(f"Failed to get environments: {response.get('errors', 'Unknown error')}")
            return []
        
        environments = response.get("data", {}).get("project", {}).get("environments", [])
        return environments
    
    def get_environment_variables(self, project_id, environment_id):
        """Get environment variables for a project environment
        
        Args:
            project_id (str): Railway project ID
            environment_id (str): Railway environment ID
            
        Returns:
            dict: Dictionary of environment variables
        """
        query = """
        query GetEnvironmentVariables($projectId: String!, $environmentId: String!) {
            project(id: $projectId) {
                environment(id: $environmentId) {
                    variables {
                        name
                        value
                    }
                }
            }
        }
        """
        
        variables = {
            "projectId": project_id,
            "environmentId": environment_id
        }
        
        response = self._request(query, variables)
        if not response or "errors" in response:
            logger.error(f"Failed to get environment variables: {response.get('errors', 'Unknown error')}")
            return {}
        
        env_vars = {}
        for var in response.get("data", {}).get("project", {}).get("environment", {}).get("variables", []):
            env_vars[var.get("name")] = var.get("value")
        
        return env_vars
    
    def set_environment_variables(self, project_id, environment_id, variables):
        """Set environment variables for a project environment
        
        Args:
            project_id (str): Railway project ID
            environment_id (str): Railway environment ID
            variables (dict): Dictionary of environment variables
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        mutation SetEnvironmentVariables($projectId: String!, $environmentId: String!, $variables: [EnvironmentVariableInput!]!) {
            environmentVariableSet(projectId: $projectId, environmentId: $environmentId, variables: $variables) {
                id
            }
        }
        """
        
        variable_inputs = []
        for name, value in variables.items():
            variable_inputs.append({
                "name": name,
                "value": value
            })
        
        variables = {
            "projectId": project_id,
            "environmentId": environment_id,
            "variables": variable_inputs
        }
        
        response = self._request(query, variables)
        if not response or "errors" in response:
            logger.error(f"Failed to set environment variables: {response.get('errors', 'Unknown error')}")
            return False
        
        return True
    
    def trigger_redeploy(self, project_id, environment_id):
        """Trigger a redeployment for a project
        
        Args:
            project_id (str): Railway project ID
            environment_id (str): Railway environment ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        mutation TriggerRedeploy($projectId: String!, $environmentId: String!) {
            deploymentTrigger(projectId: $projectId, environmentId: $environmentId) {
                id
            }
        }
        """
        
        variables = {
            "projectId": project_id,
            "environmentId": environment_id
        }
        
        response = self._request(query, variables)
        if not response or "errors" in response:
            logger.error(f"Failed to trigger redeploy: {response.get('errors', 'Unknown error')}")
            return False
        
        return True


def find_locallift_project(client):
    """Find the LocalLift project in Railway
    
    Args:
        client (RailwayAPI): Railway API client
        
    Returns:
        tuple: (project_id, environment_id) or (None, None) if not found
    """
    projects = client.get_projects()
    
    for project in projects:
        if "locallift" in project.get("name", "").lower():
            logger.info(f"Found LocalLift project: {project['name']} ({project['id']})")
            
            environments = client.get_project_environments(project["id"])
            
            # Try to find production environment first
            for env in environments:
                if env.get("name", "").lower() == "production":
                    logger.info(f"Found production environment: {env['id']}")
                    return project["id"], env["id"]
            
            # Otherwise just use the first environment
            if environments:
                logger.info(f"Using first available environment: {environments[0]['id']}")
                return project["id"], environments[0]["id"]
    
    logger.warning("Could not find LocalLift project in Railway")
    return None, None


def ensure_port_configuration(client, project_id, environment_id):
    """Ensure PORT environment variable is set correctly
    
    Args:
        client (RailwayAPI): Railway API client
        project_id (str): Railway project ID
        environment_id (str): Railway environment ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    env_vars = client.get_environment_variables(project_id, environment_id)
    
    if "PORT" not in env_vars:
        logger.info("Setting PORT environment variable to 8000")
        env_vars["PORT"] = "8000"
        return client.set_environment_variables(project_id, environment_id, {"PORT": "8000"})
    
    logger.info(f"PORT environment variable already set to {env_vars['PORT']}")
    return True


def verify_railway_deployment(endpoint_url):
    """Verify that the Railway deployment is working
    
    Args:
        endpoint_url (str): Railway deployment URL
        
    Returns:
        bool: True if working, False otherwise
    """
    logger.info(f"Verifying Railway deployment at {endpoint_url}")
    
    # Try the base URL
    try:
        response = requests.get(endpoint_url, timeout=DEFAULT_TIMEOUT)
        if 200 <= response.status_code < 400:
            logger.info(f"Railway deployment is working (Status: {response.status_code})")
            return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to connect to Railway deployment: {e}")
    
    # Try the health endpoint
    health_url = f"{endpoint_url.rstrip('/')}/health"
    try:
        response = requests.get(health_url, timeout=DEFAULT_TIMEOUT)
        if 200 <= response.status_code < 400:
            logger.info(f"Railway health endpoint is working (Status: {response.status_code})")
            return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to connect to Railway health endpoint: {e}")
    
    # Try the API endpoint
    api_url = f"{endpoint_url.rstrip('/')}/api"
    try:
        response = requests.get(api_url, timeout=DEFAULT_TIMEOUT)
        if 200 <= response.status_code < 400:
            logger.info(f"Railway API endpoint is working (Status: {response.status_code})")
            return True
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to connect to Railway API endpoint: {e}")
    
    logger.error("Railway deployment verification failed")
    return False


def configure_railway(token=None, endpoint_url=None):
    """Configure Railway deployment
    
    Args:
        token (str, optional): Railway API token
        endpoint_url (str, optional): Railway deployment URL to verify
        
    Returns:
        bool: True if successful, False otherwise
    """
    client = RailwayAPI(token)
    
    if not client.token:
        logger.warning("Railway API token not provided, skipping configuration")
        return False
    
    project_id, environment_id = find_locallift_project(client)
    
    if not project_id or not environment_id:
        logger.error("Could not find LocalLift project in Railway")
        return False
    
    # Ensure PORT configuration
    port_configured = ensure_port_configuration(client, project_id, environment_id)
    
    if not port_configured:
        logger.error("Failed to configure PORT environment variable")
        return False
    
    # Trigger redeployment
    logger.info("Triggering redeployment...")
    redeployed = client.trigger_redeploy(project_id, environment_id)
    
    if not redeployed:
        logger.error("Failed to trigger redeployment")
        return False
    
    # Wait for deployment to complete
    logger.info("Waiting for deployment to complete...")
    time.sleep(10)
    
    # Verify deployment
    if endpoint_url:
        return verify_railway_deployment(endpoint_url)
    
    return True
