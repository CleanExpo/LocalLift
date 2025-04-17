#!/bin/bash
# LocalLift Documentation Build Script
# This script builds the project documentation for deployment

echo "Building LocalLift documentation..."
echo "======================================"

# Create docs directory if it doesn't exist
mkdir -p docs/site

# Generate simple documentation index
cat > docs/site/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LocalLift Documentation</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2563eb;
        }
        a {
            color: #3b82f6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        code {
            background-color: #f1f1f1;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
        }
        pre {
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .header {
            border-bottom: 1px solid #ddd;
            margin-bottom: 20px;
            padding-bottom: 10px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>LocalLift Documentation</h1>
        <p>API and Development Reference</p>
    </div>

    <h2>Overview</h2>
    <p>
        LocalLift is a regional group CRM with gamification features, designed for local businesses and community groups to track engagement, progress, and achievements.
    </p>

    <h2>API Endpoints</h2>
    <p>The base URL for API calls depends on your environment:</p>
    <ul>
        <li>Production: <code>https://local-lift-production.up.railway.app</code></li>
        <li>Development: <code>http://localhost:8000</code></li>
    </ul>
    
    <h3>Health Check</h3>
    <p>
        Endpoint: <code>GET /api/health</code><br>
        Description: Simple health check to verify the API is operational<br>
        Response: <code>{"status": "OK", "message": "API is operational"}</code>
    </p>

    <h3>Leaderboards</h3>
    <p>
        Endpoint: <code>GET /api/leaderboard</code><br>
        Description: Get global badge leaderboard with detailed statistics<br>
    </p>
    <p>
        Endpoint: <code>GET /api/simple-leaderboard</code><br>
        Description: Get simplified badge leaderboard<br>
    </p>
    <p>
        Endpoint: <code>GET /api/simple-leaderboard/{timeframe}</code><br>
        Description: Get simplified badge leaderboard for specific timeframe<br>
        Parameters: timeframe - "week", "month", "quarter", "year", "all"
    </p>

    <h2>Frontend Configuration</h2>
    <p>
        The frontend automatically detects whether it's running in production or development and uses the appropriate API endpoint. This is managed by the <code>config.js</code> file.
    </p>
    <pre>// Example usage in frontend code
fetch(apiBase + '/api/health')
  .then(response => response.json())
  .then(data => console.log(data));</pre>

    <h2>Deployment</h2>
    <p>The application is deployed in two parts:</p>
    <ol>
        <li>Frontend: Deployed on Vercel at <a href="https://local-lift-aimh06zru-admin-cleanexpo247s-projects.vercel.app" target="_blank">Local-Lift Vercel</a></li>
        <li>Backend: Deployed on Railway at <a href="https://local-lift-production.up.railway.app" target="_blank">Local-Lift API</a></li>
    </ol>

    <div class="footer">
        &copy; 2025 LocalLift. All rights reserved.
    </div>
</body>
</html>
EOF

# Generate API documentation
echo "API documentation generated in docs/site/index.html"
echo "Documentation build complete!"
