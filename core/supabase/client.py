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
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rsooolwhapkkkwbmybdb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID", "rsooolwhapkkkwbmybdb")

if not SUPABASE_KEY:
    logger.warning("SUPABASE_KEY environment variable is not set")

def get_supabase_client() -> Client:
    """
    Get a configured Supabase client instance using anon key for public access.
    
    Returns:
        Client: A configured Supabase client with anonymous role permissions
    
    Raises:
        ValueError: If SUPABASE_KEY environment variable is not set
    """
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY environment variable is not set")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_admin_client() -> Client:
    """
    Get a configured Supabase admin client instance using service role key.
    This client has elevated permissions and should be used only for
    server-side operations that require admin access.
    
    Returns:
        Client: A configured Supabase client with service role permissions
    
    Raises:
        ValueError: If SUPABASE_SERVICE_KEY environment variable is not set
    """
    if not SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY environment variable is not set")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize default clients for convenience
try:
    supabase_client = get_supabase_client()
    logger.info("Initialized Supabase client with anonymous role")
except ValueError as e:
    logger.error(f"Failed to initialize default Supabase client: {e}")
    supabase_client = None

try:
    supabase_admin_client = get_supabase_admin_client()
    logger.info("Initialized Supabase client with service role")
except ValueError as e:
    logger.error(f"Failed to initialize admin Supabase client: {e}")
    supabase_admin_client = None
