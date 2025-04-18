"""
Database connection module.
"""
from typing import Generator, Any
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError # Import SQLAlchemyError
import sys # Import sys for exit
import os # Import os
from core.config import get_settings

settings = get_settings() # Keep settings for other parts of the app
engine = None
SessionLocal = None
Base = declarative_base()

print("--- Attempting to create database engine ---")
try:
    # Explicitly get DATABASE_URL from environment for engine creation
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("!!! FATAL: DATABASE_URL environment variable not found.", file=sys.stderr)
        sys.exit(1) # Exit if DB URL is missing
        
    print(f"--- Using DATABASE_URL from ENV: {db_url[:db_url.find('@') + 1]}... (Credentials Hidden)") # Log URL safely

    # Add connect_args for potential timeout adjustments if needed later
    engine = create_engine(
        db_url, # Use the directly fetched URL
        # connect_args={"options": "-c statement_timeout=30000"} # Example: 30 second timeout
        pool_pre_ping=True # Add pool pre-ping to check connections
    )
    # Try a simple connection to verify
    with engine.connect() as connection:
        print("--- Database engine created and connection successful ---")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except SQLAlchemyError as e:
    print(f"!!! DATABASE ENGINE CREATION FAILED: {e}", file=sys.stderr)
    # Optionally, exit if engine creation is critical for startup
    # sys.exit(1) 
except Exception as e:
    print(f"!!! UNEXPECTED ERROR DURING DB SETUP: {e}", file=sys.stderr)
    # sys.exit(1)

# Ensure SessionLocal is defined even if engine creation fails, to avoid later NameErrors
if SessionLocal is None:
     # Define a dummy sessionmaker if engine failed, so get_db doesn't raise NameError
     # This will likely cause errors later, but helps pinpoint the initial failure
     print("!!! SessionLocal not created due to engine failure. Using dummy.", file=sys.stderr)
     SessionLocal = sessionmaker() 

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.

    Yields:
        Session: SQLAlchemy database session
    """
    if SessionLocal is None:
        print("!!! ERROR: get_db called but SessionLocal is None (engine creation failed?)", file=sys.stderr)
        raise RuntimeError("Database session not initialized.")
        
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
