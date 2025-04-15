#!/bin/bash

echo "Starting Local Lift API Server..."
echo "API will be available at http://localhost:8002"
echo "----------------------------------------------------------------"
echo "Available endpoints:"
echo "  - / (Homepage)"
echo "  - /dashboard (User Dashboard)"
echo "  - /api/health (Health Check)"
echo "  - /api/gamification/levels (Gamification Levels)"
echo "  - /api/gamification/achievements (Achievements)"
echo "  - /api/leaderboards/global (Global Leaderboard)"
echo "  - /api/certifications/courses (Certification Courses)"
echo "----------------------------------------------------------------"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8002
