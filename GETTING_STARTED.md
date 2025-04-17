# Getting Started with LocalLift

This guide will help you get your LocalLift site up and running, both for local development and production deployment.

## Local Development

### 1. Start the Backend (FastAPI)

```bash
# Navigate to the LocalLift directory
cd LocalLift

# Activate your Python environment (if using one)
# Example: source venv/bin/activate

# Start the FastAPI server with hot-reload
uvicorn main:app --reload --port 8000
```

The backend will be available at: http://localhost:8000

You can access the API documentation at: http://localhost:8000/docs

### 2. Serve the Frontend

Since the frontend is a static site, you can use any static file server. For simplicity, you can use Python's built-in HTTP server:

```bash
# Navigate to the public directory
cd LocalLift/public

# Start a simple HTTP server
python -m http.server 3000
```

The frontend will be available at: http://localhost:3000

## Production Deployment

LocalLift uses a two-part deployment:
- Backend: Deployed to Railway
- Frontend: Deployed to Vercel

### 1. Deploy the Backend to Railway

```bash
# Navigate to the LocalLift directory
cd LocalLift

# Run the deployment script
./deploy-secure.sh
```

This script will:
- Authenticate with Railway
- Link your project
- Deploy the FastAPI application

### 2. Deploy the Frontend to Vercel

```bash
# Navigate to the LocalLift directory
cd LocalLift

# Run the deployment script
./deploy-vercel.sh
```

This script will:
- Build documentation if needed
- Verify configuration files
- Deploy the static site to Vercel

## Verifying Your Deployment

1. The frontend should be accessible at your Vercel domain
2. The backend API should be accessible at your Railway domain
3. The frontend should automatically connect to the backend API

## Troubleshooting

### API Connection Issues

If the frontend can't connect to the API:

1. Check that the `public/js/config.js` file has the correct API URL:
```javascript
API_BASE_URL: 'https://locallift-production.up.railway.app'
```

2. Verify that CORS is properly configured in the backend:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Static File Serving Issues

If you see 404 errors for static assets:

1. Make sure all files are in the `public` directory
2. Check that the paths in HTML files correctly reference the assets
3. Verify that the Vercel configuration is correct:
```json
{
  "cleanUrls": true,
  "rewrites": [
    { "source": "/dashboard", "destination": "/dashboard/index.html" },
    { "source": "/login", "destination": "/login/index.html" },
    { "source": "/admin/guide", "destination": "/admin/guide/index.html" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "buildCommand": "",
  "outputDirectory": "public"
}
```

## Accessing Different Pages

After deployment, you can access:

- Home page: `/`
- Dashboard: `/dashboard`
- Admin Guide: `/admin/guide`
- Login: `/login`

## API Health Check

You can verify if the API is running correctly by accessing:

```
https://your-railway-app-url.up.railway.app/api/health
```

This should return a JSON response with the status and version information.
