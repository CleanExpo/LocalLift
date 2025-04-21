"""
Railway PORT Configuration Fix

This script focuses specifically on fixing PORT-related issues in Railway deployments.
According to Railway documentation (https://docs.railway.com/guides/public-networking#railway-provided-domain),
applications must listen on the PORT environment variable for the service to be accessible.

This script will:
1. Check main.py and other potential entry points
2. Update the code to properly use the PORT environment variable
3. Create a simple test server if no suitable entry file is found
"""

import os
import sys
import re
import shutil

# Configuration
POTENTIAL_ENTRY_FILES = [
    "main.py",
    "app.py",
    "server.py",
    "api.py",
    "web_app.py",
    "simplified_main.py",
    "railway_entry.py"
]

def backup_file(file_path):
    """Create a backup of a file before modifying it"""
    backup_path = file_path + ".port.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"📦 Backed up {file_path} to {backup_path}")
    return backup_path

def find_entry_file():
    """Find the most likely entry point file"""
    print("🔍 Looking for application entry point...")
    
    # Check Procfile first if it exists
    if os.path.exists("Procfile"):
        with open("Procfile", "r") as f:
            content = f.read()
            # Look for python command
            match = re.search(r'python\s+(\S+)', content)
            if match:
                entry_file = match.group(1)
                if os.path.exists(entry_file):
                    print(f"✅ Found entry file from Procfile: {entry_file}")
                    return entry_file
    
    # Check railway.toml
    if os.path.exists("railway.toml"):
        with open("railway.toml", "r") as f:
            content = f.read()
            # Look for startCommand
            match = re.search(r'startCommand\s*=\s*"python\s+(\S+)"', content)
            if match:
                entry_file = match.group(1)
                if os.path.exists(entry_file):
                    print(f"✅ Found entry file from railway.toml: {entry_file}")
                    return entry_file
    
    # Check potential entry files
    for file in POTENTIAL_ENTRY_FILES:
        if os.path.exists(file):
            print(f"✅ Found potential entry file: {file}")
            return file
    
    print("❌ No entry file found. Will create a new one.")
    return None

def update_port_configuration(entry_file):
    """Update the file to use PORT environment variable correctly"""
    if not entry_file or not os.path.exists(entry_file):
        return False
    
    print(f"🔧 Analyzing {entry_file} for PORT configuration...")
    
    with open(entry_file, "r") as f:
        content = f.read()
    
    # Check if PORT is already correctly configured
    if re.search(r'port\s*=\s*int\s*\(\s*os\.(?:environ\.get|getenv)\s*\(\s*[\'"]PORT[\'"]\s*,', content, re.IGNORECASE):
        print(f"✅ {entry_file} already uses PORT environment variable correctly")
        return True
    
    # Make a backup
    backup_file(entry_file)
    
    # Different patterns to look for and fix
    patterns_and_replacements = [
        # Pattern for FastAPI/Uvicorn
        (
            r'(uvicorn\.run\s*\(\s*[\'"][^\'"]+(app|application)[^\'"]*[\'"]\s*,\s*)(port\s*=\s*\d+)',
            r'\1port=int(os.environ.get("PORT", 8080))'
        ),
        # Pattern for Flask
        (
            r'(app\.run\s*\(\s*)(port\s*=\s*\d+)',
            r'\1port=int(os.environ.get("PORT", 8080))'
        ),
        # Pattern for hardcoded port value
        (
            r'(port\s*=\s*)(\d+)',
            r'port = int(os.environ.get("PORT", \2))'
        )
    ]
    
    updated = False
    for pattern, replacement in patterns_and_replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True
    
    # Add os import if needed
    if updated and "import os" not in content:
        if "import" in content:
            # Add after last import
            import_lines = re.findall(r'^.*import.*$', content, re.MULTILINE)
            if import_lines:
                last_import = import_lines[-1]
                content = content.replace(last_import, last_import + "\nimport os")
        else:
            # Add at the beginning
            content = "import os\n\n" + content
    
    # Add PORT code if not found and we have some keywords indicating a web framework
    if not updated and any(keyword in content for keyword in ["Flask", "FastAPI", "uvicorn", "app", "server"]):
        print("⚠️ Couldn't find direct port configuration pattern, attempting to add one...")
        
        # Check for if __name__ == "__main__" pattern
        main_pattern = r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:'
        if re.search(main_pattern, content):
            # Add after if __name__ == "__main__":
            main_match = re.search(main_pattern, content)
            main_block_start = main_match.end()
            
            # Find the indentation
            lines = content.split('\n')
            line_num = content[:main_block_start].count('\n')
            
            # Find the indentation of the next line
            if line_num + 1 < len(lines):
                indent = re.match(r'(\s*)', lines[line_num + 1]).group(1)
            else:
                indent = "    "
            
            # Insert PORT code
            port_code = f"\n{indent}port = int(os.environ.get('PORT', 8080))\n{indent}host = '0.0.0.0'\n"
            
            # Check if there's an app.run() or uvicorn.run() to modify
            if "app.run" in content:
                # Replace app.run with app.run(host=host, port=port)
                content = re.sub(
                    r'app\.run\s*\(\s*\)',
                    f'app.run(host=host, port=port)',
                    content
                )
                # If it already has parameters, add host and port
                content = re.sub(
                    r'app\.run\s*\(\s*(.*?)\s*\)',
                    lambda m: f'app.run(host=host, port=port, {m.group(1)})' if m.group(1) else f'app.run(host=host, port=port)',
                    content
                )
            elif "uvicorn.run" in content:
                # Replace uvicorn.run with port and host
                content = re.sub(
                    r'uvicorn\.run\s*\(\s*"([^"]+)"\s*\)',
                    f'uvicorn.run("\\1", host=host, port=port)',
                    content
                )
                # If it already has parameters, add host and port
                content = re.sub(
                    r'uvicorn\.run\s*\(\s*"([^"]+)"\s*,\s*(.*?)\s*\)',
                    lambda m: f'uvicorn.run("\\1", host=host, port=port, {m.group(2)})' if m.group(2) else f'uvicorn.run("\\1", host=host, port=port)',
                    content
                )
            else:
                # Just add the PORT definition, but it might not be used
                pass
            
            # Insert after if __name__ == "__main__": line
            content_before = content[:main_block_start]
            content_after = content[main_block_start:]
            content = content_before + port_code + content_after
            updated = True
    
    if updated:
        with open(entry_file, "w") as f:
            f.write(content)
        print(f"✅ Updated {entry_file} to use PORT environment variable")
        return True
    else:
        print(f"⚠️ Could not automatically update {entry_file}. Manual changes may be needed.")
        return False

def create_simple_server():
    """Create a simple server file that listens on PORT"""
    entry_file = "railway_entry.py"
    print(f"🔧 Creating simple FastAPI server in {entry_file}...")
    
    # Create a basic FastAPI app
    content = """
import os
from fastapi import FastAPI
import uvicorn

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
    print(f"Starting server on {host}:{port}")
    uvicorn.run("railway_entry:app", host=host, port=port)
"""
    
    with open(entry_file, "w") as f:
        f.write(content.strip())
    
    print(f"✅ Created {entry_file} with proper PORT configuration")
    
    # Update Procfile
    with open("Procfile", "w") as f:
        f.write("web: python railway_entry.py")
    
    print("✅ Updated Procfile to use the new entry point")
    
    # Update railway.toml
    railway_toml_content = """[build]
builder = "nixpacks"

[deploy]
startCommand = "python railway_entry.py"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "always"
"""
    
    with open("railway.toml", "w") as f:
        f.write(railway_toml_content)
    
    print("✅ Updated railway.toml with proper configuration")
    
    return entry_file

def update_railway_config():
    """Update Railway configuration files"""
    print("\n🔧 Updating Railway configuration...")
    
    # Update Procfile if it exists but doesn't have web: prefix
    if os.path.exists("Procfile"):
        with open("Procfile", "r") as f:
            content = f.read().strip()
        
        if not content.startswith("web:"):
            # Backup original
            backup_file("Procfile")
            
            # Prepend web: if missing
            if "python" in content:
                new_content = f"web: {content}"
                with open("Procfile", "w") as f:
                    f.write(new_content)
                print("✅ Updated Procfile to include 'web:' prefix")
    
    # Update or create railway.toml
    railway_toml_content = """[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "always"
"""
    
    # If entry file is different, update railway.toml accordingly
    entry_file = find_entry_file()
    if entry_file and entry_file != "main.py":
        railway_toml_content = railway_toml_content.replace(
            'startCommand = "python main.py"',
            f'startCommand = "python {entry_file}"'
        )
    
    if os.path.exists("railway.toml"):
        backup_file("railway.toml")
    
    with open("railway.toml", "w") as f:
        f.write(railway_toml_content)
    
    print("✅ Updated railway.toml with proper configuration")

def main():
    print("=" * 50)
    print("Railway PORT Configuration Fix")
    print("=" * 50)
    print("This script fixes PORT-related issues in Railway deployments.")
    
    # Find entry file
    entry_file = find_entry_file()
    
    # Update or create entry file
    success = False
    if entry_file:
        success = update_port_configuration(entry_file)
    
    if not success:
        # Create a simple server
        entry_file = create_simple_server()
    
    # Update Railway config
    update_railway_config()
    
    print("\n" + "=" * 50)
    print("PORT CONFIGURATION FIX COMPLETE")
    print("=" * 50)
    print(f"\n📋 Entry file: {entry_file}")
    print("\n📋 Next steps:")
    print("1. Deploy your application on Railway with these changes")
    print("2. Ensure the PORT environment variable is set in Railway (it should be by default)")
    print("3. Check the logs during deployment to ensure your app starts correctly")
    print("4. Test your application at: https://local-lift-production.up.railway.app/health")
    
    print("\n⚠️ Note: If this automatic fix doesn't work, you may need to:")
    print("1. Check your application code and ensure it listens on process.env.PORT")
    print("2. Review the Railway logs for specific errors")
    print("3. Consult the Railway documentation on public networking:")
    print("   https://docs.railway.com/guides/public-networking#railway-provided-domain")

if __name__ == "__main__":
    main()
