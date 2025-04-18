import uvicorn
import os
import sys

if __name__ == "__main__":
    port_str = os.getenv("PORT")
    if port_str is None:
        print("Error: PORT environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    try:
        port = int(port_str)
    except ValueError:
        print(f"Error: Invalid PORT environment variable '{port_str}'. Must be an integer.", file=sys.stderr)
        sys.exit(1)
        
    host = os.getenv("HOST", "0.0.0.0") # Use HOST env var or default
    workers = int(os.getenv("WEB_CONCURRENCY", "2")) # Use WEB_CONCURRENCY or default
    
    print(f"--- Starting Uvicorn ---")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    
    # Use reload=False for production
    uvicorn.run("railway_entry:app", host=host, port=port, workers=workers, reload=False)
