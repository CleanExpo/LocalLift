"""
Supabase Client Configuration

This module initializes the Supabase client for server-side access.
It establishes a connection to the Supabase backend using the project URL
and API key, which should be set in environment variables.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rsooolwhapkkkwbmybdb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set")

def get_supabase_client() -> Client:
    """
    Get a configured Supabase client instance.
    
    Returns:
        Client: A configured Supabase client
    
    Raises:
        ValueError: If SUPABASE_KEY environment variable is not set
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize a default client for convenience
supabase_client = get_supabase_client()
