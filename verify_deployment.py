#!/usr/bin/env python3
"""
LocalLift CRM - Comprehensive Deployment Verification Script
-----------------------------------------------------------
This script performs automated verification of all components in the LocalLift CRM
deployment, including backend API, database connection, and frontend accessibility.

Usage:
    python verify_deployment.py [--verbose]

Options:
    --verbose    Show detailed output for each test
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deployment_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Deployment endpoints
BACKEND_URL = "https://humorous-serenity-locallift.up.railway.app"
FRONTEND_URL = "https://local-lift-lnsm8puo8-admin-cleanexpo247s-projects.vercel.app"
DATABASE_URL = "https://rsooolwhapkkkwbmybdb.supabase.co"

# API endpoints to test
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"
DB_STATUS_ENDPOINT = f"{BACKEND_URL}/database/status"
API_VERSION_ENDPOINT = f"{BACKEND_URL}/api/version"

# Test credentials (for authenticated endpoints)
TEST_USER = {
    "email": "test@locallift.com",
    "password": "TestPassword123!"
}

class DeploymentVerifier:
    """Class to verify all aspects of the deployment"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.auth_token = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend": {
                "health": False,
                "database_connection": False,
                "api_version": None
            },
            "frontend": {
                "accessible": False,
                "api_connection": False
            },
            "authentication": {
                "login": False,
                "token_valid": False
            },
            "integration": {
                "end_to_end": False
            },
            "issues": []
        }
    
    def log(self, message, level="info"):
        """Log message if verbose is enabled"""
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
    
    def check_backend_health(self):
        """Verify backend health endpoint"""
        self.log(f"Checking backend health at {HEALTH_ENDPOINT}")
        try:
            response = requests.get(HEALTH_ENDPOINT, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.results["backend"]["health"] = True
                    self.log("✅ Backend health check passed")
                    return True
                else:
                    self.log(f"❌ Backend health check failed: {data}", level="error")
            else:
                self.log(f"❌ Backend health check failed with status {response.status_code}", level="error")
        except Exception as e:
            self.log(f"❌ Error connecting to backend: {str(e)}", level="error")
            self.results["issues"].append(f"Backend health check error: {str(e)}")
        return False
    
    def check_database_connection(self):
        """Verify database connection through the API"""
        self.log(f"Checking database connection at {DB_STATUS_ENDPOINT}")
        try:
            response = requests.get(DB_STATUS_ENDPOINT, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "connected":
                    self.results["backend"]["database_connection"] = True
                    self.log("✅ Database connection check passed")
                    return True
                else:
                    self.log(f"❌ Database connection check failed: {data}", level="error")
            else:
                self.log(f"❌ Database connection check failed with status {response.status_code}", level="error")
        except Exception as e:
            self.log(f"❌ Error checking database connection: {str(e)}", level="error")
            self.results["issues"].append(f"Database connection check error: {str(e)}")
        return False
    
    def check_api_version(self):
        """Check API version information"""
        self.log(f"Checking API version at {API_VERSION_ENDPOINT}")
        try:
            response = requests.get(API_VERSION_ENDPOINT, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.results["backend"]["api_version"] = data.get("version")
                self.log(f"✅ API version check passed: {data.get('version')}")
                return True
            else:
                self.log(f"❌ API version check failed with status {response.status_code}", level="error")
        except Exception as e:
            self.log(f"❌ Error checking API version: {str(e)}", level="error")
            self.results["issues"].append(f"API version check error: {str(e)}")
        return False
    
    def check_frontend_accessibility(self):
        """Verify frontend is accessible"""
        self.log(f"Checking frontend accessibility at {FRONTEND_URL}")
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                self.results["frontend"]["accessible"] = True
                self.log("✅ Frontend accessibility check passed")
                return True
            else:
                self.log(f"❌ Frontend accessibility check failed with status {response.status_code}", level="error")
        except Exception as e:
            self.log(f"❌ Error checking frontend accessibility: {str(e)}", level="error")
            self.results["issues"].append(f"Frontend accessibility check error: {str(e)}")
        return False
    
    def test_authentication(self):
        """Test authentication flow"""
        self.log(f"Testing authentication at {BACKEND_URL}/api/auth/login")
        try:
            auth_response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json=TEST_USER,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                self.auth_token = auth_data.get("token")
                
                if self.auth_token:
                    self.results["authentication"]["login"] = True
                    self.log("✅ Authentication login check passed")
                    
                    # Verify token by calling a protected endpoint
                    me_response = requests.get(
                        f"{BACKEND_URL}/api/users/me",
                        headers={"Authorization": f"Bearer {self.auth_token}"},
                        timeout=10
                    )
                    
                    if me_response.status_code == 200:
                        self.results["authentication"]["token_valid"] = True
                        self.log("✅ Authentication token validation check passed")
                        return True
                    else:
                        self.log(f"❌ Token validation failed with status {me_response.status_code}", level="error")
                else:
                    self.log("❌ Authentication succeeded but no token returned", level="error")
            else:
                self.log(f"❌ Authentication failed with status {auth_response.status_code}", level="error")
                self.log(f"Response: {auth_response.text}", level="error")
        except Exception as e:
            self.log(f"❌ Error during authentication test: {str(e)}", level="error")
            self.results["issues"].append(f"Authentication test error: {str(e)}")
        return False
    
    def test_end_to_end(self):
        """Test an end-to-end flow"""
        if not self.auth_token:
            self.log("⚠️ Skipping end-to-end test - no valid authentication token", level="warning")
            return False
        
        self.log("Testing end-to-end flow")
        # Simplified end-to-end test - in a real scenario this would be more comprehensive
        try:
            # Just check if we can access the dashboard API with our token
            dashboard_response = requests.get(
                f"{BACKEND_URL}/api/dashboard/summary",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=10
            )
            
            if dashboard_response.status_code == 200:
                self.results["integration"]["end_to_end"] = True
                self.log("✅ End-to-end flow test passed")
                return True
            else:
                self.log(f"❌ End-to-end flow test failed with status {dashboard_response.status_code}", level="error")
        except Exception as e:
            self.log(f"❌ Error during end-to-end test: {str(e)}", level="error")
            self.results["issues"].append(f"End-to-end test error: {str(e)}")
        return False
    
    def run_all_checks(self):
        """Run all verification checks"""
        self.log("Starting comprehensive deployment verification")
        
        # Backend checks
        self.check_backend_health()
        self.check_database_connection()
        self.check_api_version()
        
        # Frontend checks
        self.check_frontend_accessibility()
        
        # Authentication and integration checks
        # Comment these out if you don't have test credentials configured
        # self.test_authentication()
        # self.test_end_to_end()
        
        self.log("Deployment verification completed")
        return self.results
    
    def generate_report(self):
        """Generate a report of the verification results"""
        # Calculate success percentage
        backend_checks = sum([
            self.results["backend"]["health"],
            self.results["backend"]["database_connection"],
            bool(self.results["backend"]["api_version"])
        ])
        frontend_checks = sum([
            self.results["frontend"]["accessible"],
            self.results["frontend"]["api_connection"]
        ])
        auth_checks = sum([
            self.results["authentication"]["login"],
            self.results["authentication"]["token_valid"]
        ])
        integration_checks = sum([
            self.results["integration"]["end_to_end"]
        ])
        
        total_checks = 6  # Adjust based on which checks you're actually running
        passed_checks = backend_checks + frontend_checks  # + auth_checks + integration_checks
        
        if total_checks > 0:
            success_rate = (passed_checks / total_checks) * 100
        else:
            success_rate = 0
        
        # Create a report
        report = {
            "timestamp": self.results["timestamp"],
            "success_rate": f"{success_rate:.1f}%",
            "backend_status": "OPERATIONAL" if backend_checks >= 2 else "ISSUES DETECTED",
            "frontend_status": "OPERATIONAL" if frontend_checks >= 1 else "ISSUES DETECTED",
            "database_status": "CONNECTED" if self.results["backend"]["database_connection"] else "CONNECTION FAILED",
            "issues": self.results["issues"],
            "details": self.results
        }
        
        # Print summary
        self.log("\n=== DEPLOYMENT VERIFICATION REPORT ===")
        self.log(f"Timestamp: {report['timestamp']}")
        self.log(f"Success Rate: {report['success_rate']}")
        self.log(f"Backend Status: {report['backend_status']}")
        self.log(f"Frontend Status: {report['frontend_status']}")
        self.log(f"Database Status: {report['database_status']}")
        
        if report["issues"]:
            self.log("\nIssues Detected:")
            for issue in report["issues"]:
                self.log(f"- {issue}")
        
        # Save to file
        with open("DEPLOYMENT_TEST_RESULTS.md", "w") as f:
            f.write("# LocalLift Deployment Verification Results\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"* **Success Rate:** {report['success_rate']}\n")
            f.write(f"* **Backend Status:** {report['backend_status']}\n")
            f.write(f"* **Frontend Status:** {report['frontend_status']}\n")
            f.write(f"* **Database Status:** {report['database_status']}\n\n")
            
            if report["issues"]:
                f.write("## Issues Detected\n\n")
                for issue in report["issues"]:
                    f.write(f"* {issue}\n")
            
            f.write("\n## Detailed Results\n\n")
            f.write("### Backend Checks\n\n")
            f.write(f"* Health Check: {'✅ PASSED' if self.results['backend']['health'] else '❌ FAILED'}\n")
            f.write(f"* Database Connection: {'✅ PASSED' if self.results['backend']['database_connection'] else '❌ FAILED'}\n")
            f.write(f"* API Version: {self.results['backend']['api_version'] or 'Not Available'}\n\n")
            
            f.write("### Frontend Checks\n\n")
            f.write(f"* Accessibility: {'✅ PASSED' if self.results['frontend']['accessible'] else '❌ FAILED'}\n")
            f.write(f"* API Connection: {'✅ PASSED' if self.results['frontend']['api_connection'] else '❌ FAILED'}\n\n")
            
            # Include full JSON data for debugging
            f.write("\n## Raw Results\n\n")
            f.write("```json\n")
            f.write(json.dumps(self.results, indent=2))
            f.write("\n```\n")
        
        return report

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="LocalLift CRM Deployment Verification")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    verifier = DeploymentVerifier(verbose=args.verbose)
    results = verifier.run_all_checks()
    report = verifier.generate_report()
    
    # Determine exit code based on critical checks
    if (results["backend"]["health"] and 
        results["backend"]["database_connection"] and 
        results["frontend"]["accessible"]):
        logger.info("✅ Critical checks passed - deployment is operational")
        sys.exit(0)
    else:
        logger.error("❌ Critical checks failed - deployment has issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
