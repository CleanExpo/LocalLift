# LocalLift

## 📦 Deployment Status

![CI/CD](https://github.com/CleanExpo/LocalLift/actions/workflows/main.yml/badge.svg)

## Project Overview

LocalLift is a comprehensive platform designed to help local businesses improve their online presence and customer engagement through automated tools, analytics, and educational resources.

## Environment Setup

The project has been configured with all necessary environment variables:

- **Supabase**: Database and authentication
- **SendGrid**: Email services 
- **Railway**: Deployment infrastructure

## Deployment

The application is automatically deployed through GitHub Actions CI/CD pipeline, with current status displayed by the badge above.

### Deployment Options

- **Production**: Railway platform deployment
- **Documentation**: Vercel static hosting

## Getting Started

1. **Prerequisites**
   - Python 3.10+
   - Node.js 16+
   - Docker (optional for local development)

2. **Environment Configuration**
   - Copy `.env.template` to `.env` 
   - Run `python tools/env_check.py` to verify your configuration

3. **Local Development**
   ```bash
   # Start the application
   python main.py
   # OR
   ./start.sh  # macOS/Linux
   ./start.bat # Windows
   ```

4. **Build & Deployment**
   ```bash
   # For documentation
   bash tools/doc_build.sh  # macOS/Linux
   
   # For application
   ./deploy.sh  # Standard deployment
   ./deploy-secure.sh  # Deployment with sensitive operations
   ```

## Project Structure

- `/apps`: Application modules for different user types and features
- `/core`: Core functionality and configurations
- `/docs`: Documentation source files
- `/public`: Static assets for Vercel hosting
- `/supabase`: Database schema and migrations
- `/templates`: HTML templates
- `/tools`: Utility scripts for development and deployment

## Environment Management

Use the included validation tool to ensure all environment variables are properly configured:

```bash
python tools/env_check.py
```

This will verify all required credentials for Supabase, SendGrid, and Railway are properly set.
