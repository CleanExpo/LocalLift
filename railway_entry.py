"""
Local Lift - Railway Deployment Entry Point
"""
import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback
    uvicorn.run("main:app", host="0.0.0.0", port=port)
