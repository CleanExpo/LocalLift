# Supabase MCP Integration for LocalLift CRM

This document provides detailed instructions on integrating and using the Supabase Model Context Protocol (MCP) server with the LocalLift CRM system to manage role-based access control and other database operations.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Schema Setup](#database-schema-setup)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Security Considerations](#security-considerations)

## Introduction

### What is Supabase MCP?

The Supabase MCP server enables direct interaction with your Supabase database through an MCP interface, allowing AI assistants and development tools to perform database operations, manage users, and handle roles and permissions directly.

### Benefits for LocalLift CRM

- **Streamlined Development**: Interact with your database directly from AI assistants or development environments
- **Role Management**: Easily manage user roles and permissions
- **Data Access**: Query and modify data with proper access controls
- **Schema Management**: Create and modify database tables and relationships
- **Authentication**: Interact with Supabase authentication system

## Installation

### Prerequisites

- Node.js v14+ installed
- Access to a Supabase project
- Supabase project URL and service role key
- MCP-compatible client (such as Cline or Cursor)

### Steps

1. **Create MCP server directory**:

```bash
mkdir supabase-mcp
cd supabase-mcp
```

2. **Initialize Node.js project**:

```bash
npm init -y
```

3. **Install dependencies**:

```bash
npm install @supabase/supabase-js @modelcontextprotocol/sdk
```

4. **Create server file** (index.js):

```javascript
#!/usr/bin/env node

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
```

5. **Make the server executable**:

```bash
chmod +x index.js
```

## Configuration

### Setting Up MCP Client

For Cline or other MCP-compatible clients, you need to configure the server in your settings file:

```json
{
  "mcpServers": {
    "supabase": {
      "autoApprove": [],
      "disabled": false,
      "timeout": 60,
      "command": "node",
      "args": ["/path/to/supabase-mcp/index.js"],
      "env": {
        "SUPABASE_URL": "https://yourprojectid.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      },
      "transportType": "stdio"
    }
  }
}
```

### LocalLift CRM Configuration

For LocalLift specifically, place the MCP server in the following location:

```
C:\Users\PhillMcGurk\OneDrive - Disaster Recovery\Documents\Cline\MCP\supabase-mcp
```

And use these Supabase credentials:

```
SUPABASE_URL=https://rsooolwhapkkkwbmybdb.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJzb29vbHdoYXBra2t3Ym15YmRiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDcwODU0NiwiZXhwIjoyMDYwMjg0NTQ2fQ.4z9OqyeU9-CHmDtZwA87ymicFEM-U53yzdeTZwc6KdE
```

## Database Schema Setup

The Supabase MCP server requires specific database tables and functions to support role-based access control. Run the following SQL script in your Supabase SQL editor:

```sql
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
```

## Usage Examples

### Interacting with the MCP Server

Once your MCP server is configured, you can use it through supported tools like Cline or Cursor.

#### Checking a User's Role

```javascript
// Example of using the MCP server to check a user's role
const userId = "550e8400-e29b-41d4-a716-446655440000"; // Example UUID
const result = await mcp.get_user_role({ userId });
console.log(result.role); // Expected output: "user", "staff", "manager", "admin", or "superadmin"
```

#### Setting a User's Role

```javascript
// Example of using the MCP server to set a user's role
const userId = "550e8400-e29b-41d4-a716-446655440000"; // Example UUID
const role = "manager";
const result = await mcp.set_user_role({ userId, role });
console.log(result.success); // Expected output: true
console.log(result.message); // Expected output: "User role set to manager"
```

#### Checking User Permissions

```javascript
// Example of using the MCP server to check if a user has a specific permission
const userId = "550e8400-e29b-41d4-a716-446655440000"; // Example UUID
const permission = "view_analytics";
const result = await mcp.check_user_permission({ userId, permission });
console.log(result.hasPermission); // Expected output: true or false
console.log(result.source); // Expected output: "role" or "temporary"
```

#### Executing SQL Queries

```javascript
// Example of using the MCP server to execute a SQL query
const query = "SELECT * FROM public.user_roles WHERE role = $1";
const params = ["admin"];
const result = await mcp.execute_sql({ query, params });
console.log(result.result); // Expected output: Array of admin users
```

### Integration with LocalLift Frontend

In the LocalLift frontend, you can use the MCP server through utility functions:

```javascript
// Example utility function to check user permissions
async function hasPermission(permission) {
  const user = auth.getCurrentUser();
  if (!user) return false;
  
  try {
    const result = await mcp.check_user_permission({
      userId: user.id,
      permission
    });
    return result.hasPermission;
  } catch (error) {
    console.error("Error checking permission:", error);
    return false;
  }
}

// Usage in UI components
if (await hasPermission('view_analytics')) {
  // Show analytics component
  renderAnalyticsPanel();
}
```

## Troubleshooting

### Common Issues

#### Connection Issues

**Problem**: MCP server cannot connect to Supabase

**Solution**:
- Verify your Supabase URL and service role key
- Check network connectivity
- Ensure your Supabase project is active

#### Permission Errors

**Problem**: User doesn't have access to expected features

**Solution**:
- Verify the user's role in the `user_roles` table
- Check the permission mappings in the `checkUserPermission` function
- Ensure the user's JWT token contains the role claim

#### SQL Execution Errors

**Problem**: SQL queries fail to execute

**Solution**:
- Verify that the `execute_sql` function exists in your Supabase database
- Check that your queries are properly formatted
- Ensure parameters are correctly supplied

### Logging and Debugging

To enable debug logs in the MCP server, add the following code to your index.js file:

```javascript
// Add debug logging
const DEBUG = process.env.DEBUG === 'true';

function debugLog(...args) {
  if (DEBUG) {
    console.error('[DEBUG]', ...args);
  }
}

// Then use debugLog throughout your code
debugLog('Executing query:', query, params);
```

Then run the server with the DEBUG environment variable:

```bash
DEBUG=true node index.js
```

## Advanced Configuration

### Custom Role Definitions

You can customize the role hierarchy and permissions by modifying the `rolePermissions` object in the `checkUserPermission` method:

```javascript
const rolePermissions = {
  'user': ['view_dashboard', 'edit_profile', 'view_learning'],
  // Add custom role
  'customer': ['view_dashboard', 'edit_profile', 'view_learning', 'place_orders'],
  'staff': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports'],
  'manager': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users'],
  'admin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs'],
  'superadmin': ['view_dashboard', 'edit_profile', 'view_learning', 'view_analytics', 'view_reports', 'manage_users', 'edit_settings', 'view_admin_panel', 'view_audit_logs']
};
```

Don't forget to update the SQL schema as well:

```sql
ALTER TABLE public.user_roles 
  DROP CONSTRAINT user_roles_role_check,
  ADD CONSTRAINT user_roles_role_check 
    CHECK (role IN ('user', 'customer', 'staff', 'manager', 'admin', 'superadmin'));
```

### Adding Custom Tools

You can add custom tools to the MCP server by extending the `tools` array in the `ListToolsRequestSchema` handler and adding a corresponding case in the `CallToolRequestSchema` handler:

```javascript
// Add to tools array
{
  name: 'get_user_activity',
  description: 'Get a user\'s recent activity',
  inputSchema: {
    type: 'object',
    properties: {
      userId: {
        type: 'string',
        description: 'The user ID to check'
      },
      limit: {
        type: 'number',
        description: 'Maximum number of activities to return',
        default: 10
      }
    },
    required: ['userId']
  }
}

// Add to switch statement
case 'get_user_activity':
  result = await this.getUserActivity(args.userId, args.limit || 10);
  break;

// Add new method
async getUserActivity(userId, limit) {
  try {
    const { data, error } = await supabase
      .from('access_logs')
      .select('*')
      .eq('user_id', userId)
      .order('timestamp', { ascending: false })
      .limit(limit);

    if (error) throw error;
    return { activities: data };
  } catch (error) {
    console.error('Error getting user activity:', error);
    throw error;
  }
}
```

## Security Considerations

### Service Role Key Protection

The Supabase service role key has full access to your database. Protect it carefully:

- Never commit it to version control
- Store it securely in environment variables
- Restrict its use to trusted environments

### SQL Injection Prevention

The MCP server includes basic protection against SQL injection, but you should enhance this for production use:

```javascript
async executeSql(query, params) {
  try {
    // More comprehensive security checks
    const disallowedPatterns = [
      /drop\s+table/i,
      /truncate\s+table/i,
      /delete\s+from/i,
      /alter\s+table/i,
      /grant\s+/i,
      /revoke\s+/i
    ];
    
    for (const pattern of disallowedPatterns) {
      if (pattern.test(query)) {
        throw new Error(`Operation not allowed: ${pattern.toString()}`);
      }
    }
    
    // Execute the query with parameterized inputs
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
```

### Access Control

When deploying to production, implement additional access control:

1. **IP restrictions**: Limit which IP addresses can use the MCP server
2. **Request rate limiting**: Prevent abuse by limiting request rates
3. **Audit logging**: Log all MCP operations for security review

---

This documentation provides a comprehensive guide to setting up and using the Supabase MCP server with the LocalLift CRM system. For additional assistance, refer to the Supabase documentation or contact the LocalLift development team.
