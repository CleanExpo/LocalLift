import uvicorn
import os
import sys
import json # Import json
import traceback

def log_secure_env_vars():
    """Log environment variables without exposing sensitive data"""
    try:
        # Create a filtered copy of environment variables
        env_copy = dict(os.environ)
        # Hide sensitive values in environment variables
        sensitive_keys = ['TOKEN', 'SECRET', 'PASSWORD', 'KEY', 'AUTH']
        for key in env_copy:
            for sensitive_key in sensitive_keys:
                if sensitive_key.upper() in key.upper():
                    env_copy[key] = "********" # Mask sensitive values
        
        # Print essential environment info
        print("--- Environment Info ---")
        print(f"PORT: {'Set' if 'PORT' in env_copy else 'Not Set'}")
        print(f"HOST: {env_copy.get('HOST', '0.0.0.0')}")
        print(f"ENVIRONMENT: {env_copy.get('ENVIRONMENT', 'Not Set')}")
        print(f"WEB_CONCURRENCY: {env_copy.get('WEB_CONCURRENCY', '2')}")
        print("--- End Environment Info ---")
    except Exception as e:
        print(f"Could not process environment variables: {e}", file=sys.stderr)

def validate_environment():
    """Validate critical environment variables"""
    critical_vars = []
    
    # Check PORT - critical for server binding
    port_str = os.getenv("PORT")
    if port_str is None:
        critical_vars.append("PORT")
        port = 8080  # Default port if not set
    else:
        try:
            port = int(port_str)
        except ValueError:
            print(f"!!! Error: Invalid PORT value '{port_str}'. Must be an integer.", file=sys.stderr)
            sys.exit(1)
    
    # Report if any critical variables are missing
    if critical_vars:
        print(f"!!! Warning: The following environment variables are not set: {', '.join(critical_vars)}", file=sys.stderr)
        print(f"Using default values where possible.", file=sys.stderr)
    
    return {
        "port": port,
        "host": os.getenv("HOST", "0.0.0.0"),
        "workers": int(os.getenv("WEB_CONCURRENCY", "2")),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

if __name__ == "__main__":
    try:
        print("=== LocalLift Server Starting ===")
        
        # Validate environment and get configuration
        config = validate_environment()
        
        # Log sanitized environment variables
        log_secure_env_vars()
        
        # Display server configuration
        print(f"=== Server Configuration ===")
        print(f"Host: {config['host']}")
        print(f"Port: {config['port']}")
        print(f"Workers: {config['workers']}")
        print(f"Environment: {config['environment']}")
        
        # Use reload only in development environment
        reload_mode = config['environment'].lower() == 'development'
        
        # Start the server
        print(f"=== Starting Uvicorn (reload={'enabled' if reload_mode else 'disabled'}) ===")
        uvicorn.run(
            "railway_entry:app", 
            host=config['host'], 
            port=config['port'], 
            workers=config['workers'], 
            reload=reload_mode
        )
    except Exception as e:
        print(f"!!! Critical Error: {e}", file=sys.stderr)
        print("Stack trace:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
