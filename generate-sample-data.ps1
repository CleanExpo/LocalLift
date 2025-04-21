# Sample Data Generation Script for LocalLift CRM
# This script generates instructions to create test data in Supabase

# Function to display section header
function Show-Header {
    param (
        [string]$title
    )
    Write-Host "`n=========================================================================" -ForegroundColor Cyan
    Write-Host " $title" -ForegroundColor Cyan
    Write-Host "=========================================================================" -ForegroundColor Cyan
}

# Start execution
Clear-Host
Show-Header "LocalLift CRM Sample Data Generator"
Write-Host "This script will help you generate sample data in your Supabase database."
Write-Host "This data is useful for UI/UX testing and initial deployment verification."

# Create samples directory if it doesn't exist
if (-not (Test-Path ".\samples")) {
    New-Item -ItemType Directory -Path ".\samples" | Out-Null
    Write-Host "Created samples directory." -ForegroundColor Green
}

# Create sample user roles SQL file
$userRolesSQL = @"
-- Sample User Roles
-- Replace the placeholder UUIDs with actual user IDs from your Supabase Auth > Users table
-- Create a normal user (if you already created a superadmin)
INSERT INTO public.user_roles (user_id, role) 
VALUES ('11111111-1111-1111-1111-111111111111', 'user');

-- Create a staff user
INSERT INTO public.user_roles (user_id, role) 
VALUES ('22222222-2222-2222-2222-222222222222', 'staff');

-- Create a manager user
INSERT INTO public.user_roles (user_id, role) 
VALUES ('33333333-3333-3333-3333-333333333333', 'manager');

-- Create an admin user
INSERT INTO public.user_roles (user_id, role) 
VALUES ('44444444-4444-4444-4444-444444444444', 'admin');

-- The superadmin should already exist from the deployment process
"@
$userRolesSQL | Out-File -FilePath ".\samples\01_user_roles.sql" -Encoding utf8

# Create sample user profiles SQL file
$userProfilesSQL = @"
-- Create sample user profiles 
-- Replace the placeholder UUIDs with actual user IDs from your Supabase Auth > Users table
INSERT INTO public.user_profiles (user_id, phone, job_title, company, bio, last_login) 
VALUES 
('11111111-1111-1111-1111-111111111111', '555-123-4567', 'User', 'Customer Company', 'Regular user account', NOW()),
('22222222-2222-2222-2222-222222222222', '555-234-5678', 'Staff Member', 'LocalLift', 'Staff account with basic privileges', NOW()),
('33333333-3333-3333-3333-333333333333', '555-345-6789', 'Team Manager', 'LocalLift', 'Manager account with team management privileges', NOW()),
('44444444-4444-4444-4444-444444444444', '555-456-7890', 'Administrator', 'LocalLift', 'Administrator with system configuration access', NOW()),
('YOUR-SUPERADMIN-UUID', '555-567-8901', 'Super Administrator', 'LocalLift', 'Super admin with complete system access', NOW());

-- Create sample user preferences
INSERT INTO public.user_preferences (user_id, theme, dashboard_layout, notifications, language, timezone) 
VALUES 
('11111111-1111-1111-1111-111111111111', 'light', '{"widgets": ["recent_activity", "calendar"]}', '{"email": true, "push": false}', 'en', 'America/Los_Angeles'),
('22222222-2222-2222-2222-222222222222', 'dark', '{"widgets": ["tasks", "customers", "calendar"]}', '{"email": true, "push": true}', 'en', 'America/Chicago'),
('33333333-3333-3333-3333-333333333333', 'light', '{"widgets": ["team", "tasks", "analytics"]}', '{"email": true, "push": true}', 'en', 'America/New_York'),
('44444444-4444-4444-4444-444444444444', 'dark', '{"widgets": ["system", "users", "analytics"]}', '{"email": true, "push": true}', 'en', 'America/Phoenix'),
('YOUR-SUPERADMIN-UUID', 'dark', '{"widgets": ["system", "users", "analytics", "logs"]}', '{"email": true, "push": true}', 'en', 'UTC');
"@
$userProfilesSQL | Out-File -FilePath ".\samples\02_user_profiles.sql" -Encoding utf8

# Create sample customers SQL file
$customersSQL = @"
-- Create sample customers
-- Replace the placeholder UUIDs with actual user IDs from your Supabase Auth > Users table
INSERT INTO public.customers (name, email, phone, company, status, assigned_to, created_by) 
VALUES 
('John Smith', 'john.smith@example.com', '555-111-2222', 'ABC Company', 'active', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333'),
('Jane Doe', 'jane.doe@example.com', '555-222-3333', 'XYZ Corp', 'active', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333'),
('Bob Johnson', 'bob.johnson@example.com', '555-333-4444', 'Acme Inc', 'active', '33333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333'),
('Alice Williams', 'alice.williams@example.com', '555-444-5555', 'Local Business LLC', 'active', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444'),
('Charlie Brown', 'charlie.brown@example.com', '555-555-6666', 'Main Street Shop', 'lead', '22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222'),
('Diana Miller', 'diana.miller@example.com', '555-666-7777', 'Downtown Cafe', 'prospect', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333'),
('Edward Davis', 'edward.davis@example.com', '555-777-8888', 'Tech Solutions', 'active', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444'),
('Fiona Garcia', 'fiona.garcia@example.com', '555-888-9999', 'Creative Studio', 'inactive', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444'),
('George Martinez', 'george.martinez@example.com', '555-999-0000', 'Auto Repair Shop', 'churned', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333'),
('Hannah Lee', 'hannah.lee@example.com', '555-000-1111', 'Health Clinic', 'active', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444');
"@
$customersSQL | Out-File -FilePath ".\samples\03_customers.sql" -Encoding utf8

# Create sample interactions SQL file
$interactionsSQL = @"
-- Create sample customer interactions
-- First get the customer IDs created above
DO $$
DECLARE
    customer_ids UUID[];
    customer_count INTEGER;
    user_ids UUID[];
    current_customer_id UUID;
    current_user_id UUID;
    interaction_types TEXT[] := ARRAY['email', 'call', 'meeting', 'note', 'other'];
    random_type TEXT;
    random_date TIMESTAMP;
BEGIN
    -- Get customer IDs
    SELECT ARRAY_AGG(id) INTO customer_ids FROM public.customers;
    customer_count := array_length(customer_ids, 1);
    
    -- Get user IDs with staff, manager, or admin roles
    SELECT ARRAY_AGG(user_id) INTO user_ids FROM public.user_roles 
    WHERE role IN ('staff', 'manager', 'admin', 'superadmin');
    
    -- Create 30 random interactions
    FOR i IN 1..30 LOOP
        -- Select random customer
        current_customer_id := customer_ids[1 + floor(random() * customer_count)::INT];
        
        -- Select random user
        current_user_id := user_ids[1 + floor(random() * array_length(user_ids, 1))::INT];
        
        -- Select random interaction type
        random_type := interaction_types[1 + floor(random() * 5)::INT];
        
        -- Generate random date in the last 30 days
        random_date := NOW() - (random() * INTERVAL '30 days');
        
        -- Insert the interaction
        INSERT INTO public.customer_interactions 
        (customer_id, user_id, type, content, scheduled_at, completed_at)
        VALUES 
        (
            current_customer_id, 
            current_user_id, 
            random_type, 
            CASE 
                WHEN random_type = 'email' THEN 'Email conversation about new services'
                WHEN random_type = 'call' THEN 'Phone call to discuss account status'
                WHEN random_type = 'meeting' THEN 'In-person meeting to review business needs'
                WHEN random_type = 'note' THEN 'Note about customer preferences'
                ELSE 'Other interaction with customer'
            END,
            random_date,
            CASE
                WHEN random() > 0.3 THEN random_date + (random() * INTERVAL '3 days')
                ELSE NULL
            END
        );
    END LOOP;
END $$;
"@
$interactionsSQL | Out-File -FilePath ".\samples\04_interactions.sql" -Encoding utf8

# Instructions
Show-Header "Sample Data Generated"
Write-Host "Sample SQL files have been created in the 'samples' directory:" -ForegroundColor Green
Write-Host "- 01_user_roles.sql - Creates test users with different roles"
Write-Host "- 02_user_profiles.sql - Creates profiles and preferences for test users"
Write-Host "- 03_customers.sql - Creates sample customer records"
Write-Host "- 04_interactions.sql - Creates sample customer interactions"
Write-Host "`nTo use these files:" -ForegroundColor Yellow
Write-Host "1. Log in to Supabase dashboard: https://rsooolwhapkkkwbmybdb.supabase.co"
Write-Host "2. Navigate to SQL Editor"
Write-Host "3. Create a new query"
Write-Host "4. Open and copy from each SQL file"
Write-Host "5. IMPORTANT: Replace the placeholder UUIDs with actual user IDs from your Auth > Users table"
Write-Host "6. Execute each query file in order (01, 02, 03, 04)"
Write-Host "`nThis sample data will help you verify UI/UX functionality for the CRM system."

# Offer to open Supabase
$response = Read-Host "`nWould you like to open the Supabase dashboard now? (y/n)"
if ($response.ToLower() -eq "y") {
    Write-Host "Opening Supabase dashboard..." -ForegroundColor Yellow
    Start-Process "https://rsooolwhapkkkwbmybdb.supabase.co"
}

Write-Host "`nSample data generation complete!" -ForegroundColor Green
