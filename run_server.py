import uvicorn
import os
import sys
import json # Import json

if __name__ == "__main__":
    # --- DIAGNOSTIC: Print all environment variables ---
    print("--- All Environment Variables ---")
    try:
        # Use json.dumps for cleaner formatting, sort keys
        print(json.dumps(dict(os.environ), indent=2, sort_keys=True))
    except Exception as e:
        print(f"Could not dump environment variables: {e}")
    print("--- End Environment Variables ---")
    # --- END DIAGNOSTIC ---

    port_str = os.getenv("PORT")
    if port_str is None:
        print("!!! Error: PORT environment variable not set.", file=sys.stderr)
        # Don't exit immediately, let it try to continue to see other errors
        port = 8080 # Default port if not set, though it will likely fail later
        print("!!! Warning: PORT not found, defaulting to 8080", file=sys.stderr)
    else:
        try:
            port = int(port_str)
        except ValueError:
            print(f"!!! Error: Invalid PORT environment variable '{port_str}'. Must be an integer.", file=sys.stderr)
            sys.exit(1) # Exit if PORT is invalid
        
    host = os.getenv("HOST", "0.0.0.0") # Use HOST env var or default
    workers = int(os.getenv("WEB_CONCURRENCY", "2")) # Use WEB_CONCURRENCY or default
    
    print(f"--- Starting Uvicorn ---")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    
    # Use reload=False for production
    uvicorn.run("railway_entry:app", host=host, port=port, workers=workers, reload=False)
