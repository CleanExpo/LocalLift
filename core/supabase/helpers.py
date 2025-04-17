"""
Supabase Helper Functions

This module provides utility functions for common Supabase operations,
making it easier to work with the Supabase client throughout the application.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from .client import supabase_client, get_supabase_client

logger = logging.getLogger(__name__)

# Authentication helpers
def sign_up_user(email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict:
    """
    Sign up a new user with email and password
    
    Args:
        email: User's email address
        password: User's password
        user_metadata: Optional metadata for the user
        
    Returns:
        Dictionary containing user data and session
        
    Raises:
        Exception: If sign up fails
    """
    try:
        user_metadata = user_metadata or {}
        response = supabase_client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": user_metadata
            }
        })
        return response
    except Exception as e:
        logger.error(f"Error signing up user: {e}")
        raise


def sign_in_user(email: str, password: str) -> Dict:
    """
    Sign in an existing user with email and password
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary containing user data and session
        
    Raises:
        Exception: If sign in fails
    """
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        logger.error(f"Error signing in user: {e}")
        raise


def sign_out_user() -> None:
    """
    Sign out the current user
    
    Raises:
        Exception: If sign out fails
    """
    try:
        supabase_client.auth.sign_out()
    except Exception as e:
        logger.error(f"Error signing out user: {e}")
        raise


def get_current_user() -> Optional[Dict]:
    """
    Get the current authenticated user
    
    Returns:
        User data or None if not authenticated
    """
    try:
        response = supabase_client.auth.get_user()
        return response.user if response else None
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


# Database helpers
def fetch_data(table: str, 
               columns: str = "*", 
               filters: Optional[Dict] = None, 
               order_by: Optional[Dict] = None, 
               limit: Optional[int] = None, 
               offset: Optional[int] = None) -> List[Dict]:
    """
    Fetch data from a Supabase table with filtering, ordering, and pagination
    
    Args:
        table: Name of the table to query
        columns: Columns to select (default: "*" for all)
        filters: Dictionary of filters to apply (field: value)
        order_by: Dictionary of ordering {column: direction} where direction is 'asc' or 'desc'
        limit: Maximum number of rows to return
        offset: Number of rows to skip
        
    Returns:
        List of records matching the query
        
    Raises:
        Exception: If the query fails
    """
    try:
        query = supabase_client.table(table).select(columns)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        # Apply ordering
        if order_by:
            for column, direction in order_by.items():
                if direction.lower() == 'asc':
                    query = query.order(column)
                else:
                    query = query.order(column, desc=True)
        
        # Apply pagination
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching data from {table}: {e}")
        raise


def insert_data(table: str, data: Union[Dict, List[Dict]]) -> Dict:
    """
    Insert data into a Supabase table
    
    Args:
        table: Name of the table
        data: Dictionary or list of dictionaries to insert
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        Exception: If the insertion fails
    """
    try:
        response = supabase_client.table(table).insert(data).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error inserting data into {table}: {e}")
        raise


def update_data(table: str, data: Dict, filters: Dict) -> Dict:
    """
    Update data in a Supabase table
    
    Args:
        table: Name of the table
        data: Dictionary containing the fields to update
        filters: Dictionary of filters to identify records to update
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        Exception: If the update fails
    """
    try:
        query = supabase_client.table(table).update(data)
        
        # Apply filters
        for field, value in filters.items():
            query = query.eq(field, value)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Error updating data in {table}: {e}")
        raise


def delete_data(table: str, filters: Dict) -> Dict:
    """
    Delete data from a Supabase table
    
    Args:
        table: Name of the table
        filters: Dictionary of filters to identify records to delete
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        Exception: If the deletion fails
    """
    try:
        query = supabase_client.table(table).delete()
        
        # Apply filters
        for field, value in filters.items():
            query = query.eq(field, value)
        
        response = query.execute()
        return response.data
    except Exception as e:
        logger.error(f"Error deleting data from {table}: {e}")
        raise


# Storage helpers
def upload_file(bucket: str, path: str, file_content, file_options: Optional[Dict] = None) -> Dict:
    """
    Upload a file to Supabase Storage
    
    Args:
        bucket: Name of the storage bucket
        path: Path within the bucket
        file_content: Content of the file to upload
        file_options: Optional file metadata
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        Exception: If the upload fails
    """
    try:
        response = supabase_client.storage.from_(bucket).upload(
            path,
            file_content,
            file_options
        )
        return response
    except Exception as e:
        logger.error(f"Error uploading file to {bucket}/{path}: {e}")
        raise


def get_file_url(bucket: str, path: str, options: Optional[Dict] = None) -> str:
    """
    Get the public URL for a file in Supabase Storage
    
    Args:
        bucket: Name of the storage bucket
        path: Path within the bucket
        options: Optional URL generation options
        
    Returns:
        Public URL for the file
        
    Raises:
        Exception: If getting the URL fails
    """
    try:
        return supabase_client.storage.from_(bucket).get_public_url(path, options)
    except Exception as e:
        logger.error(f"Error getting URL for {bucket}/{path}: {e}")
        raise


def download_file(bucket: str, path: str) -> bytes:
    """
    Download a file from Supabase Storage
    
    Args:
        bucket: Name of the storage bucket
        path: Path within the bucket
        
    Returns:
        File content as bytes
        
    Raises:
        Exception: If the download fails
    """
    try:
        response = supabase_client.storage.from_(bucket).download(path)
        return response
    except Exception as e:
        logger.error(f"Error downloading file from {bucket}/{path}: {e}")
        raise


def delete_file(bucket: str, paths: Union[str, List[str]]) -> Dict:
    """
    Delete a file or files from Supabase Storage
    
    Args:
        bucket: Name of the storage bucket
        paths: Single path or list of paths to delete
        
    Returns:
        Dictionary containing the response data
        
    Raises:
        Exception: If the deletion fails
    """
    try:
        if isinstance(paths, str):
            paths = [paths]
        response = supabase_client.storage.from_(bucket).remove(paths)
        return response
    except Exception as e:
        logger.error(f"Error deleting file(s) from {bucket}: {e}")
        raise
