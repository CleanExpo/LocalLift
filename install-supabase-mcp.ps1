# Install Supabase MCP Server for LocalLift CRM
# This script sets up a Supabase MCP server to help manage role-based access control

Write-Host "Installing Supabase MCP Server for LocalLift CRM..." -ForegroundColor Cyan

# Set up directory for Supabase MCP
$mcpDir = "C:\Users\PhillMcGurk\OneDrive - Disaster Recovery\Documents\Cline\MCP"
$supaMcpDir = "$mcpDir\supabase-mcp"

# Create directory if it doesn't exist
if (-not (Test-Path -Path $supaMcpDir)) {
    Write-Host "Creating directory: $supaMcpDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $supaMcpDir -Force | Out-Null
}

# Navigate to the directory
Set-Location -Path $supaMcpDir

# Create package.json
Write-Host "Creating package.json..." -ForegroundColor Blue
$packageJson = @'
{
  "name": "supabase-mcp",
  "version": "1.0.0",
  "description": "Supabase MCP Server for LocalLift CRM",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "keywords": [
    "supabase",
    "mcp",
    "crm",
    "locallift"
  ],
  "author": "LocalLift Team",
  "license": "MIT"
}
'@

Set-Content -Path "$supaMcpDir\package.json" -Value $packageJson

# Create index.js - the main MCP server file
Write-Host "Creating index.js..." -ForegroundColor Blue
$indexJs = @'
#!/usr/bin/env node

/**
 * Supabase MCP Server for LocalLift CRM
 * This server provides MCP access to Supabase for RBAC functionality
 */

const { createClient } = require('@supabase/supabase-js');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

// Environment variables
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required');
  process.exit(1);
}

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

class SupabaseMcpServer {
  constructor() {
    this.server = new Server(
      {
        name: 'supabase-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'get_user_role',
          description: 'Get a user\'s role from the database',
          inputSchema: {
            type: 'object',
            properties: {
              userId: {
                type: 'string',
                description: 'The user ID to check'
              }
            },
            required: ['userId']
          }
        },
        {
          name: 'set_user_role',
          description: 'Set a user\'s role in the database',
          inputSchema: {
            type: 'object',
            properties: {
              userId: {
                type: 'string',
                description: 'The user ID to update'
              },
              role: {
                type: 'string',
                description: 'The role to assign (user, staff, manager, admin, superadmin)'
              }
            },
            required: ['userId', 'role']
          }
        },
        {
          name: 'check_user_permission',
          description: 'Check if a user has a specific permission',
          inputSchema: {
            type: 'object',
            properties: {
              userId: {
                type: 'string',
                description: 'The user ID to check'
              },
              permission: {
                type: 'string',
                description: 'The permission to check for'
              }
            },
            required: ['userId', 'permission']
          }
        },
        {
          name: 'execute_sql',
          description: 'Execute a SQL query on the Supabase database',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'The SQL query to execute'
              },
              params: {
                type: 'array',
                items: {
                  type: 'string'
                },
                description: 'Query parameters (optional)'
              }
            },
            required: ['query']
          }
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result;

        switch (name) {
          case 'get_user_role':
            result = await this.getUserRole(args.userId);
            break;
          case 'set_user_role':
            result = await this.setUserRole(args.userId, args.role);
            break;
          case 'check_user_permission':
            result = await this.checkUserPermission(args.userId, args.permission);
            break;
          case 'execute_sql':
            result = await this.executeSql(args.query, args.params || []);
            break;
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error) {
        console.error(`Error executing tool ${name}:`, error);
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message || 'Unknown error'}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async getUserRole(userId) {
    try {
      const { data, error } = await supabase
        .from('user_roles')
        .select('role')
        .eq('user_id', userId)
        .single();

      if (error) throw error;
      return { role: data?.role || 'user' };
    } catch (error) {
      console.error('Error getting user role:', error);
      throw error;
    }
  }

  async setUserRole(userId, role) {
    try {
      const validRoles = ['user', 'staff', 'manager', 'admin', 'superadmin'];
      if (!validRoles.includes(role)) {
        throw new Error(`Invalid role: ${role}. Must be one of: ${validRoles.join(', ')}`);
      }

      // Check if user exists in user_roles table
      const { data: existingRole } = await supabase
        .from('user_roles')
        .select('*')
        .eq('user_id', userId)
        .single();

      let result;
      if (existingRole) {
        // Update existing role
        const { data, error } = await supabase
          .from('user_roles')
          .update({ role })
          .eq('user_id', userId);

        if (error) throw error;
        result = { success: true, message: `User role updated to ${role}` };
      } else {
        // Insert new role
        const { data, error } = await supabase
          .from('user_roles')
          .insert([{ user_id: userId, role }]);

        if (error) throw error;
        result = { success: true, message: `User role set to ${role}` };
      }

      return result;
    } catch (error) {
      console.error('Error setting user role:', error);
      throw error;
    }
  }

  async checkUserPermission(userId, permission) {
    try {
      // First, get the user's role
      const { role } = await this.getUserRole(userId);
      
      // Define permission hierarchy
      const rolePermissions = {
        'user': ['view_dashboard', 'edit_profile', 'view_learning'],
        'staff': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports'],
        'manager': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users'],
        'admin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs'],
        'superadmin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs']
      };

      // Check if user has permission
      const hasPermission = rolePermissions[role]?.includes(permission) || false;
      
      // Also check for temporary permissions
      const { data: tempPermission } = await supabase
        .from('temp_permissions')
        .select('*')
        .eq('user_id', userId)
        .eq('permission', permission)
        .gt('expiry', new Date().toISOString())
        .single();

      return { 
        hasPermission: hasPermission || !!tempPermission,
        source: tempPermission ? 'temporary' : 'role'
      };
    } catch (error) {
      console.error('Error checking user permission:', error);
      throw error;
    }
  }

  async executeSql(query, params) {
    try {
      // Simple security check - prevent destructive queries
      const lowerQuery = query.toLowerCase();
      if (lowerQuery.includes('drop table') || lowerQuery.includes('truncate table')) {
        throw new Error('Destructive operations are not allowed');
      }

      // Execute the query
      const { data, error } = await supabase.rpc('execute_sql', {
        query_text: query,
        query_params: params
      });

      if (error) throw error;
      return { result: data };
    } catch (error) {
      console.error('Error executing SQL:', error);
      throw error;
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Supabase MCP server running on stdio');
  }
}

const server = new SupabaseMcpServer();
server.run().catch(console.error);
'@

Set-Content -Path "$supaMcpDir\index.js" -Value $indexJs

# Create SQL migration for RBAC tables
Write-Host "Creating SQL migration for RBAC tables..." -ForegroundColor Blue
$sqlMigration = @'
-- Migration: Create tables for role-based access control
-- This should be run on your Supabase database

-- Table for storing user roles
CREATE TABLE IF NOT EXISTS public.user_roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'staff', 'manager', 'admin', 'superadmin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- Table for storing user teams/hierarchy
CREATE TABLE IF NOT EXISTS public.user_teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  manager_id UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id, manager_id)
);

-- Table for storing temporary permissions
CREATE TABLE IF NOT EXISTS public.temp_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  permission TEXT NOT NULL,
  granted_by UUID REFERENCES auth.users(id) NOT NULL,
  expiry TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Table for storing role change logs
CREATE TABLE IF NOT EXISTS public.role_change_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  old_role TEXT NOT NULL,
  new_role TEXT NOT NULL,
  changed_by UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Table for storing access logs
CREATE TABLE IF NOT EXISTS public.access_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  resource TEXT NOT NULL,
  action TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  successful BOOLEAN DEFAULT true,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Function to check if a user has a specific role
CREATE OR REPLACE FUNCTION public.user_has_role(user_id UUID, required_role TEXT)
RETURNS BOOLEAN AS $$
DECLARE
  user_role TEXT;
BEGIN
  SELECT role INTO user_role FROM public.user_roles WHERE user_id = user_has_role.user_id;
  
  -- Role hierarchy
  CASE 
    WHEN required_role = 'user' THEN
      RETURN user_role IN ('user', 'staff', 'manager', 'admin', 'superadmin');
    WHEN required_role = 'staff' THEN
      RETURN user_role IN ('staff', 'manager', 'admin', 'superadmin');
    WHEN required_role = 'manager' THEN
      RETURN user_role IN ('manager', 'admin', 'superadmin');
    WHEN required_role = 'admin' THEN
      RETURN user_role IN ('admin', 'superadmin');
    WHEN required_role = 'superadmin' THEN
      RETURN user_role = 'superadmin';
    ELSE
      RETURN FALSE;
  END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to execute SQL (for MCP server)
CREATE OR REPLACE FUNCTION public.execute_sql(query_text TEXT, query_params TEXT[] DEFAULT '{}'::TEXT[])
RETURNS JSONB AS $$
DECLARE
  result JSONB;
BEGIN
  EXECUTE query_text INTO result USING query_params;
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add role claim to JWT token
CREATE OR REPLACE FUNCTION public.add_role_to_jwt()
RETURNS trigger AS $$
DECLARE
  role_val TEXT;
BEGIN
  -- Get the user's role
  SELECT role INTO role_val FROM public.user_roles WHERE user_id = auth.uid();
  
  -- If no role found, default to 'user'
  IF role_val IS NULL THEN
    role_val := 'user';
  END IF;
  
  -- Add role to the new token
  NEW.payload := jsonb_set(
    NEW.payload,
    '{role}',
    to_jsonb(role_val)
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add trigger for setting role in JWT token
DROP TRIGGER IF EXISTS add_role_to_jwt ON auth.tokens;
CREATE TRIGGER add_role_to_jwt
  BEFORE INSERT ON auth.tokens
  FOR EACH ROW
  EXECUTE PROCEDURE public.add_role_to_jwt();

-- Function to log user access
CREATE OR REPLACE FUNCTION public.log_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.access_logs (user_id, resource, action)
  VALUES (auth.uid(), TG_TABLE_NAME, TG_OP);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on all RBAC tables
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.temp_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_change_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY;

-- Create policies for user_roles table
CREATE POLICY view_own_role ON public.user_roles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY admin_manage_roles ON public.user_roles
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'superadmin')
    )
  );

-- Create policies for user_teams table
CREATE POLICY view_own_team ON public.user_teams
  FOR SELECT USING (auth.uid() = user_id OR auth.uid() = manager_id);

CREATE POLICY manager_manage_team ON public.user_teams
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('manager', 'admin', 'superadmin')
    )
  );

-- Comments for better understanding
COMMENT ON TABLE public.user_roles IS 'Stores user roles for RBAC';
COMMENT ON TABLE public.user_teams IS 'Defines manager-user relationships';
COMMENT ON TABLE public.temp_permissions IS 'Temporary permission grants';
COMMENT ON TABLE public.role_change_logs IS 'Audit logs for role changes';
COMMENT ON TABLE public.access_logs IS 'Audit logs for resource access';
'@

Set-Content -Path "$supaMcpDir\rbac_migration.sql" -Value $sqlMigration

# Create an .npmrc file to ensure proper installation
$npmrc = @'
engine-strict=false
legacy-peer-deps=true
'@
Set-Content -Path "$supaMcpDir\.npmrc" -Value $npmrc

# Install dependencies
Write-Host "Installing dependencies (this may take a minute)..." -ForegroundColor Yellow
Set-Location -Path $supaMcpDir
npm install --save @supabase/supabase-js @modelcontextprotocol/sdk

# Update MCP Settings File
Write-Host "Updating MCP settings in Cline..." -ForegroundColor Blue
$mcpSettingsPath = "c:\Users\PhillMcGurk\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json"

if (Test-Path $mcpSettingsPath) {
    $mcpSettings = Get-Content -Raw $mcpSettingsPath | ConvertFrom-Json
    
    # Add Supabase MCP server to the configuration
    $mcpSettings.mcpServers | Add-Member -NotePropertyName "supabase" -NotePropertyValue @{
        "autoApprove" = @()
        "disabled" = $false
        "timeout" = 60
        "command" = "node"
        "args" = @("$supaMcpDir\index.js")
        "env" = @{
            "SUPABASE_URL" = "https://rsooolwhapkkkwbmybdb.supabase.co"
            "SUPABASE_SERVICE_ROLE_KEY" = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE"
        }
        "transportType" = "stdio"
    } -Force
    
    # Save the updated configuration
    $mcpSettings | ConvertTo-Json -Depth 10 | Set-Content $mcpSettingsPath
    Write-Host "MCP settings updated successfully." -ForegroundColor Green
} else {
    Write-Host "MCP settings file not found at: $mcpSettingsPath" -ForegroundColor Red
    Write-Host "You'll need to manually add the Supabase MCP server configuration." -ForegroundColor Yellow
}

# Return to the original directory
Set-Location -Path "C:\Users\PhillMcGurk\Desktop\LocalLift"

# Final instructions
Write-Host "`nSupabase MCP Server has been successfully installed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Run the SQL migration in your Supabase project to create the RBAC tables" -ForegroundColor White
Write-Host "   - The migration file is located at: $supaMcpDir\rbac_migration.sql" -ForegroundColor White
Write-Host "2. Restart Cline to activate the Supabase MCP Server" -ForegroundColor White
Write-Host "3. Update your LocalLift frontend to implement the RBAC UI components" -ForegroundColor White
Write-Host "4. Update your LocalLift API endpoints to enforce role-based access" -ForegroundColor White

Write-Host "`nYou can now manage role-based access control using the Supabase MCP Server tools:" -ForegroundColor Cyan
Write-Host "- get_user_role: Get a user's role" -ForegroundColor White
Write-Host "- set_user_role: Set a user's role" -ForegroundColor White
Write-Host "- check_user_permission: Check if a user has a specific permission" -ForegroundColor White
Write-Host "- execute_sql: Execute SQL queries against your Supabase database" -ForegroundColor White
