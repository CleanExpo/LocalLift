"""
Railway entry point for the LocalLift backend

This file simply imports and re-exports the main FastAPI application
instance configured in main.py, making it accessible for the Procfile command.
"""

# Import the configured FastAPI app instance from main.py
from main import app

# The Procfile command `uvicorn railway_entry:app ...` will now correctly
# find and run the application instance defined in main.py.
# No further configuration is needed here as it's handled in main.py.

if __name__ == "__main__":
    # This block is mainly for local testing if needed,
    # Railway uses the Procfile command directly.
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    # Note: Running this file directly might have different behavior
    # regarding environment variables compared to Railway's execution.
    # Use `uvicorn main:app --reload` for local development.
    uvicorn.run("railway_entry:app", host="0.0.0.0", port=port, reload=False)
