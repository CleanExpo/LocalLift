"""
Railway Deployment Fix

This script fixes common Railway deployment issues:
1. Creates a proper health endpoint
2. Ensures the correct entrypoint is used
3. Updates the Railway configuration

Run this script to update your application files and prepare for redeployment.
"""

import os
import sys
import shutil

# Configuration
MAIN_PY_PATH = os.path.join(".", "main.py")
RAILWAY_TOML_PATH = os.path.join(".", "railway.toml")
PROCFILE_PATH = os.path.join(".", "Procfile")

def create_health_endpoint():
    """Create or update main.py to include a health endpoint"""
    print("🔧 Creating/updating health endpoint in main.py...")
    
    # Check if main.py exists
    if not os.path.exists(MAIN_PY_PATH):
        print(f"❌ {MAIN_PY_PATH} does not exist. Creating a new one...")
        with open(MAIN_PY_PATH, "w") as f:
            f.write("""from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"message": "LocalLift API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port)
""")
        print("✅ Created new main.py with health endpoint")
    else:
        # Read existing main.py
        with open(MAIN_PY_PATH, "r") as f:
            content = f.read()
        
        # Check if health endpoint already exists
        if "@app.get(\"/health\")" in content or "app.get('/health'" in content:
            print("✅ Health endpoint already exists in main.py")
        else:
            # Try to find a good place to add the health endpoint
            if "app = FastAPI()" in content:
                # Add after app = FastAPI()
                content = content.replace(
                    "app = FastAPI()",
                    """app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}"""
                )
            elif "app = Flask(__name__)" in content:
                # Add after app = Flask(__name__)
                content = content.replace(
                    "app = Flask(__name__)",
                    """app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}"""
                )
            else:
                # Add at the end and hope for the best
                content += """

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
"""
            
            # Backup original
            backup_path = MAIN_PY_PATH + ".bak"
            shutil.copy2(MAIN_PY_PATH, backup_path)
            print(f"📦 Backed up original main.py to {backup_path}")
            
            # Write updated content
            with open(MAIN_PY_PATH, "w") as f:
                f.write(content)
            
            print("✅ Added health endpoint to main.py")

def update_procfile():
    """Create or update Procfile to use the correct command"""
    print("\n🔧 Creating/updating Procfile...")
    
    procfile_content = "web: python main.py"
    
    if os.path.exists(PROCFILE_PATH):
        # Backup existing Procfile
        backup_path = PROCFILE_PATH + ".bak"
        shutil.copy2(PROCFILE_PATH, backup_path)
        print(f"📦 Backed up original Procfile to {backup_path}")
        
        # Read existing Procfile
        with open(PROCFILE_PATH, "r") as f:
            existing_content = f.read().strip()
        
        if "python main.py" in existing_content:
            print("✅ Procfile already has the correct command")
            return
    
    # Write the correct content
    with open(PROCFILE_PATH, "w") as f:
        f.write(procfile_content)
    
    print(f"✅ Updated Procfile with: {procfile_content}")

def update_railway_toml():
    """Update railway.toml with correct configuration"""
    print("\n🔧 Creating/updating railway.toml...")
    
    railway_toml_content = """[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "always"

"""
    
    if os.path.exists(RAILWAY_TOML_PATH):
        # Backup existing railway.toml
        backup_path = RAILWAY_TOML_PATH + ".bak"
        shutil.copy2(RAILWAY_TOML_PATH, backup_path)
        print(f"📦 Backed up original railway.toml to {backup_path}")
    
    # Write the correct content
    with open(RAILWAY_TOML_PATH, "w") as f:
        f.write(railway_toml_content)
    
    print(f"✅ Updated railway.toml with deployment configuration")

def verify_port_listening():
    """Verify that main.py listens on the correct PORT from environment variable"""
    print("\n🔍 Verifying PORT usage in main.py...")
    
    if not os.path.exists(MAIN_PY_PATH):
        print(f"❌ {MAIN_PY_PATH} does not exist")
        return
    
    with open(MAIN_PY_PATH, "r") as f:
        content = f.read()
    
    if "port = int(os.environ.get(\"PORT\", " in content or "port = int(os.getenv(\"PORT\", " in content:
        print("✅ main.py already uses PORT from environment variables")
    else:
        # Try to find where the port is set
        port_fixed = False
        if "uvicorn.run" in content:
            # Try to update uvicorn.run with port from env
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "uvicorn.run" in line and "port" in line:
                    lines[i] = line.replace("port=8000", "port=int(os.environ.get(\"PORT\", 8080))")
                    port_fixed = True
                    break
            
            if port_fixed:
                # Backup original
                backup_path = MAIN_PY_PATH + ".port.bak"
                shutil.copy2(MAIN_PY_PATH, backup_path)
                print(f"📦 Backed up original main.py to {backup_path}")
                
                # Write updated content
                with open(MAIN_PY_PATH, "w") as f:
                    f.write("\n".join(lines))
                
                print("✅ Updated main.py to use PORT from environment variables")
            else:
                print("⚠️ Could not automatically update PORT usage. Please ensure your application listens on the port specified by the PORT environment variable.")
        else:
            print("⚠️ Could not automatically update PORT usage. Please ensure your application listens on the port specified by the PORT environment variable.")

def main():
    print("=" * 50)
    print("Railway Deployment Fix")
    print("=" * 50)
    print("This script will update your application files to fix common deployment issues.")
    print("Backup files will be created for any files that are modified.")
    
    # Create or update the health endpoint
    create_health_endpoint()
    
    # Update Procfile
    update_procfile()
    
    # Update railway.toml
    update_railway_toml()
    
    # Verify PORT usage
    verify_port_listening()
    
    print("\n" + "=" * 50)
    print("DEPLOYMENT FIX COMPLETE")
    print("=" * 50)
    print("\n📋 Next steps:")
    print("1. Commit these changes to your repository")
    print("2. Push the changes to GitHub")
    print("3. Redeploy your application on Railway")
    print("4. Check the logs for any deployment errors")
    print("5. Test your application at: https://local-lift-production.up.railway.app/health")
    
    print("\n⚠️ Important note:")
    print("If you have a custom entry point file other than main.py,")
    print("you will need to manually update the Procfile and railway.toml to use your file.")

if __name__ == "__main__":
    main()
