# Apply Supabase Migration for LocalLift CRM
# This script applies the RBAC schema migration to your Supabase instance

Write-Host "LocalLift CRM - Applying Supabase Migration" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Configuration
$migrationFile = "./supabase/migrations/20250419_rbac_schema_fixed.sql"
$supabaseUrl = "https://rsooolwhapkkkwbmybdb.supabase.co"
$supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE"

# Check if the migration file exists
if (-not (Test-Path $migrationFile)) {
    Write-Host "Error: Migration file not found at $migrationFile" -ForegroundColor Red
    exit 1
}

# Load environment variables from .env.railway if it exists
if (Test-Path ".env.railway") {
    Get-Content ".env.railway" | ForEach-Object {
        if ($_ -match "SUPABASE_URL=(.*)") {
            $supabaseUrl = $matches[1]
        }
        if ($_ -match "SUPABASE_SERVICE_ROLE_KEY=(.*)") {
            $supabaseKey = $matches[1]
        }
    }
}

# If environment variables are still empty, prompt for them
if ([string]::IsNullOrEmpty($supabaseUrl)) {
    $supabaseUrl = Read-Host "Enter your Supabase URL (e.g., https://yourproject.supabase.co)"
}

if ([string]::IsNullOrEmpty($supabaseKey)) {
    $supabaseKey = Read-Host "Enter your Supabase service role key"
}

Write-Host "`nPreparing to apply migration..." -ForegroundColor Yellow

# Read the SQL file
$sql = Get-Content $migrationFile -Raw

Write-Host "Migration contains $(($sql -split "`n").Length) lines of SQL code." -ForegroundColor Gray

# Function to execute SQL on Supabase
function Execute-SQL {
    param (
        [string]$query
    )
    
    $headers = @{
        "apikey" = $supabaseKey
        "Authorization" = "Bearer $supabaseKey"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        "query" = $query
    } | ConvertTo-Json
    
    $endpoint = "$supabaseUrl/rest/v1/rpc/execute_sql"
    
    try {
        $response = Invoke-RestMethod -Uri $endpoint -Method POST -Headers $headers -Body $body
        return $response
    }
    catch {
        Write-Host "Error executing SQL: $_" -ForegroundColor Red
        return $null
    }
}

# Split SQL into batches to execute
function Execute-SQLBatches {
    param (
        [string]$sql
    )
    
    # Split on semicolons, but keep CREATE FUNCTION blocks intact
    $inFunction = $false
    $currentBatch = ""
    $batches = @()
    
    foreach ($line in $sql -split "`n") {
        # Check if this is the start of a function declaration
        if ($line -match "CREATE OR REPLACE FUNCTION") {
            $inFunction = $true
        }
        
        # Add line to current batch
        $currentBatch += "$line`n"
        
        # Check if this is the end of a function declaration
        if ($inFunction -and $line -match "LANGUAGE plpgsql") {
            $inFunction = $false
        }
        
        # If not in a function and line ends with semicolon, end the batch
        if (-not $inFunction -and $line -match ";$") {
            $batches += $currentBatch
            $currentBatch = ""
        }
    }
    
    # Add any remaining content as a batch
    if ($currentBatch.Trim() -ne "") {
        $batches += $currentBatch
    }
    
    # Execute each batch
    $totalBatches = $batches.Count
    $successCount = 0
    
    for ($i = 0; $i -lt $totalBatches; $i++) {
        $batch = $batches[$i]
        if ($batch.Trim() -eq "") { continue }
        
        Write-Host "Executing batch $($i+1) of $totalBatches..." -ForegroundColor Yellow
        
        $result = Execute-SQL -query $batch
        if ($result -ne $null) {
            $successCount++
            Write-Host "Batch $($i+1) executed successfully." -ForegroundColor Green
        }
        else {
            Write-Host "Batch $($i+1) failed. Continuing with next batch..." -ForegroundColor Red
        }
    }
    
    return $successCount
}

# Apply the migration
Write-Host "`nApplying database schema migration to Supabase..." -ForegroundColor Cyan

$successCount = Execute-SQLBatches -sql $sql

Write-Host "`nMigration complete!" -ForegroundColor Green
Write-Host "Successfully executed $successCount SQL batches." -ForegroundColor Green

# Final instructions
Write-Host "`nNext steps for deployment:" -ForegroundColor Cyan
Write-Host "1. Verify the Railway deployment completed successfully" -ForegroundColor White
Write-Host "2. Test the connection to Supabase from Railway" -ForegroundColor White
Write-Host "3. Set up a superadmin user in Supabase by executing:" -ForegroundColor White
Write-Host "   INSERT INTO public.user_roles (user_id, role)" -ForegroundColor Yellow
Write-Host "   VALUES ('your-user-id', 'superadmin');" -ForegroundColor Yellow
Write-Host "4. Rerun the verify-deployment.ps1 script to check if everything is working" -ForegroundColor White

Write-Host "`nMigration and configuration complete!" -ForegroundColor Green
