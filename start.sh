#!/bin/bash
echo "Starting Local Lift Dev Server..."
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8002
