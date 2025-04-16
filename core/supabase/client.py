"""
Supabase Client Configuration

This module initializes the Supabase client for server-side access.
It establishes a connection to the Supabase backend using the project URL
and API keys, which should be set in environment variables.
"""

import os
import logging
from dotenv import load_dotenv
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID")

# Log configuration status with environment check
if not SUPABASE_URL:
    logger.warning("SUPABASE_URL environment variable is not set")
if not SUPABASE_ANON_KEY:
    logger.warning("SUPABASE_ANON_KEY environment variable is not set")
if not SUPABASE_SERVICE_KEY:
    logger.warning("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")
if not SUPABASE_PROJECT_ID:
    logger.warning("SUPABASE_PROJECT_ID environment variable is not set")

def get_supabase_client() -> Client:
    """
    Get a configured Supabase client instance using anon key for public access.
    
    Returns:
        Client: A configured Supabase client with anonymous role permissions
    
    Raises:
        ValueError: If SUPABASE_ANON_KEY environment variable is not set
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is not set")
    if not SUPABASE_ANON_KEY:
        raise ValueError("SUPABASE_ANON_KEY environment variable is not set")
    
    logger.debug(f"Creating Supabase client with URL: {SUPABASE_URL}")
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_admin_client() -> Client:
    """
    Get a configured Supabase admin client instance using service role key.
    This client has elevated permissions and should be used only for
    server-side operations that require admin access.
    
    Returns:
        Client: A configured Supabase client with service role permissions
    
    Raises:
        ValueError: If SUPABASE_SERVICE_ROLE_KEY environment variable is not set
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is not set")
    if not SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set")
    
    logger.debug(f"Creating Supabase admin client with URL: {SUPABASE_URL}")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize default clients for convenience
try:
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase_client = get_supabase_client()
        logger.info(f"Initialized Supabase client with anonymous role for URL: {SUPABASE_URL}")
    else:
        logger.warning("Skipping Supabase client initialization due to missing credentials")
        supabase_client = None
except ValueError as e:
    logger.error(f"Failed to initialize default Supabase client: {e}")
    supabase_client = None
except Exception as e:
    logger.error(f"Unexpected error initializing Supabase client: {str(e)}")
    supabase_client = None

try:
    if SUPABASE_URL and SUPABASE_SERVICE_KEY:
        supabase_admin_client = get_supabase_admin_client()
        logger.info(f"Initialized Supabase admin client with service role for URL: {SUPABASE_URL}")
    else:
        logger.warning("Skipping Supabase admin client initialization due to missing credentials")
        supabase_admin_client = None
except ValueError as e:
    logger.error(f"Failed to initialize admin Supabase client: {e}")
    supabase_admin_client = None
except Exception as e:
    logger.error(f"Unexpected error initializing Supabase admin client: {str(e)}")
    supabase_admin_client = None
