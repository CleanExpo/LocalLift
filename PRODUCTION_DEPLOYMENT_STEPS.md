# Production Deployment Steps for LocalLift CRM

This guide provides a comprehensive, step-by-step process to complete the production deployment of LocalLift CRM with security enhancements and global timezone support.

## Prerequisites

Before beginning the production deployment, ensure you have:

- Access to Railway dashboard
- Access to Vercel dashboard
- Access to Supabase dashboard
- All required deployment files in the LocalLift directory
- Admin credentials for the master account

## Step 1: Deploy the Backend API with Security Enhancements

### 1.1. Update Database Schema with RBAC and Security

```bash
# Run the deployment script
cd LocalLift
.\final-deployment.ps1
```

Follow the script prompts through Step 1 and Step 2 to:
- Fix the Railway-Supabase connection
- Apply the RBAC schema to Supabase

### 1.2. Implement Security Headers

Add these security headers to the backend API by updating the main.py file:

```python
# Add these middleware to your FastAPI app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["locallift-production.up.railway.app", "yourdomain.com"]
)

# CORS with proper settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://local-lift-adjm0ahjv-admin-cleanexpo247s-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://rsooolwhapkkkwbmybdb.supabase.co;"
    return response
```

### 1.3. Enable Rate Limiting

Add rate limiting to prevent abuse:

```python
# Add this to your FastAPI app
from fastapi import Depends, HTTPException, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

@app.on_event("startup")
async def startup():
    redis_connection = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    await FastAPILimiter.init(redis_connection)

# Apply rate limiting to endpoints
@app.get("/api/sensitive-endpoint", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def sensitive_endpoint():
    return {"message": "Rate limited endpoint"}
```

### 1.4. Update Environment Variables

Update the Railway environment variables with enhanced security settings:

```
JWT_SECRET_KEY=superSecretJWTKeyForLocalLiftRBAC2025
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 1.5. Redeploy the Backend

```bash
# Deploy the updated backend to Railway
.\deploy-railway.ps1
```

## Step 2: Create SuperAdmin Account with Enhanced Security

Continue with Step 3 in the deployment script:

```bash
# Continue the deployment script if you paused
.\final-deployment.ps1
```

Follow the prompts to:
- Create your master admin account
- Assign the superadmin role
- Verify the credentials work

### 2.1. Configure Account Security Settings

After creating the admin account, add additional security settings by executing this SQL in Supabase:

```sql
-- Create security settings for the admin account
INSERT INTO public.user_security_settings 
(user_id, mfa_enabled, password_expires_at, failed_login_attempts, last_password_change) 
VALUES 
('YOUR-ADMIN-USER-ID', false, NOW() + INTERVAL '90 days', 0, NOW());
```

## Step 3: Implement Global Timezone Support

### 3.1. Update User Preferences Schema

Verify and update the timezone field in the user_preferences table:

```sql
-- Verify timezone field exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_preferences' 
AND column_name = 'timezone';

-- If it doesn't exist, add it
ALTER TABLE public.user_preferences 
ADD COLUMN IF NOT EXISTS timezone TEXT DEFAULT 'UTC';
```

### 3.2. Add Timezone Selection to Frontend

Create the timezone selector component in your frontend:

1. Create a new file: `/static/js/timezone-selector.js`
2. Implement the timezone selection code from the GLOBAL_TIMEZONE_SUPPORT.md document

### 3.3. Update User Profile Page

Modify the user profile page to include timezone selection:

1. Update `/public/settings/index.html` to include the timezone selector
2. Add the timezone selector initialization to the page's JavaScript

### 3.4. Update User Creation Flow

Ensure new users are created with proper timezone detection:

1. Update the registration form to detect and store user's timezone
2. Add timezone selection as part of the user onboarding flow

### 3.5. Update Date Display Components

Implement timezone-aware date formatting throughout the application:

1. Create a date utilities file: `/static/js/date-utils.js`
2. Update all date/time displays in the application to use these utilities

## Step 4: Secure Frontend Deployment

### 4.1. Update Content Security Policy

Create or update the security headers for your Vercel deployment:

1. Create a `vercel.json` file with security headers:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://locallift-production.up.railway.app https://rsooolwhapkkkwbmybdb.supabase.co;"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ]
}
```

### 4.2. Update Client-Side Security

Enhance client-side security by implementing:

1. Input validation and sanitization
2. XSS protection
3. CSRF protection with tokens

Add a security utility file:

```javascript
// security-utils.js
const securityUtils = {
  sanitizeInput(input) {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },
  
  validateEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase());
  },
  
  generateCSRFToken() {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }
};
```

### 4.3. Redeploy Frontend with Security Enhancements

```bash
# Deploy the updated frontend to Vercel
.\deploy-vercel.ps1
```

## Step 5: Final Verification and UI/UX Testing

Continue with Step 4, 5, and 6 in the deployment script:

```bash
# Continue the deployment script
.\final-deployment.ps1
```

Follow the prompts to:
- Verify deployment
- Generate sample data
- Perform UI/UX verification

### 5.1. Security Verification

Conduct security testing on the deployed application:

1. HTTPS verification
2. Authentication testing
3. Role-based access control testing
4. API endpoint security testing

Use the SECURITY_GUIDELINES.md document as a checklist for verification.

### 5.2. Global Timezone Verification

Test the global timezone features:

1. Set your account to different timezones
2. Verify that dates and times are displayed correctly
3. Test timezone conversion in reports and dashboards
4. Verify that timezone selection works properly

## Step 6: Post-Deployment Steps

### 6.1. Configure Monitoring & Alerting

Set up monitoring and alerting for the production environment:

1. Set up application performance monitoring
2. Configure error tracking
3. Set up security monitoring
4. Implement uptime monitoring
5. Configure alerting for critical issues

### 6.2. Backup Procedures

Establish regular backup procedures:

1. Configure daily Supabase database backups
2. Set up backup retention policies
3. Test backup restoration procedure
4. Document backup and recovery processes

### 6.3. Documentation

Finalize documentation for administrators and users:

1. Complete user guide
2. Create administrator guide
3. Document security protocols
4. Create maintenance procedures
5. Update technical documentation

### 6.4. Final Handover

Prepare for system handover:

1. User training
2. Administrator training
3. Support process establishment
4. Knowledge transfer sessions
5. Maintenance schedule setup

## Production Readiness Checklist

Complete this checklist before announcing the system as production-ready:

- [ ] Backend API deployed with security enhancements
- [ ] SuperAdmin account created and secured
- [ ] Global timezone support implemented and tested
- [ ] Frontend deployed with security headers
- [ ] All verification tests passed
- [ ] Monitoring and alerting configured
- [ ] Backup procedures established
- [ ] Documentation completed
- [ ] Training and handover completed

## Support and Maintenance

After deployment, follow these ongoing maintenance practices:

1. Regular security updates
2. Performance monitoring and optimization
3. Database maintenance
4. User support processes
5. Feature enhancement planning

By following these comprehensive production deployment steps, your LocalLift CRM will be fully operational with enhanced security, global timezone support, and enterprise-ready features.
