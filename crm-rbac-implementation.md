# Role-Based Access Control (RBAC) Implementation for LocalLift CRM

This document outlines the implementation plan for role-based access control in the LocalLift CRM system using Supabase authentication and the Supabase MCP Server for enhanced functionality.

## RBAC System Design

### 1. Role Hierarchy

LocalLift CRM will have the following role hierarchy:

```
- SuperAdmin
  - Admin
    - Manager
      - Staff
        - User
```

### 2. Permission Matrix

| Feature/Section        | SuperAdmin | Admin | Manager | Staff | User |
|------------------------|:----------:|:-----:|:-------:|:-----:|:----:|
| **Dashboard**          |     ✓      |   ✓   |    ✓    |   ✓   |  ✓   |
| **User Management**    |     ✓      |   ✓   |    ✓    |   ✗   |  ✗   |
| **System Settings**    |     ✓      |   ✓   |    ✗    |   ✗   |  ✗   |
| **Analytics**          |     ✓      |   ✓   |    ✓    |   ✓   |  ✗   |
| **Reports**            |     ✓      |   ✓   |    ✓    |   ✓   |  ✗   |
| **Learning Resources** |     ✓      |   ✓   |    ✓    |   ✓   |  ✓   |
| **Admin Panel**        |     ✓      |   ✓   |    ✗    |   ✗   |  ✗   |
| **Audit Logs**         |     ✓      |   ✓   |    ✗    |   ✗   |  ✗   |
| **Profile Management** |     ✓      |   ✓   |    ✓    |   ✓   |  ✓   |

## Implementation Strategy

### 1. Authentication with Supabase

1. **JWT Custom Claims**: Implement custom JWT claims to store user roles
2. **Auth Hooks**: Use Supabase Auth Hooks to add the role claim during authentication

```sql
-- Example: Creating an Auth Hook for adding roles to JWT
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, role)
  values (new.id, 'user'); -- Default role
  return new;
end;
$$ language plpgsql security definer;

-- Trigger the function on user creation
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

### 2. PostgreSQL RLS (Row-Level Security)

Implement Row-Level Security policies in PostgreSQL for data access control:

```sql
-- Example: RLS policy for users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see only themselves
CREATE POLICY user_view_self ON users
    FOR SELECT
    USING (auth.uid() = id);

-- Policy: Managers can see users they manage
CREATE POLICY manager_view_team ON users
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM user_teams
            WHERE manager_id = auth.uid() AND user_id = users.id
        )
    );

-- Policy: Admins can see all users
CREATE POLICY admin_view_all ON users
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM user_roles
            WHERE user_id = auth.uid() AND role IN ('admin', 'superadmin')
        )
    );
```

### 3. Frontend Implementation

1. **Role-Based Routing**: Implement route guards based on user roles

```javascript
// Example React route guard
const ProtectedRoute = ({ requiredRoles, children }) => {
  const { user, userRole } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (!requiredRoles.includes(userRole)) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
};
```

2. **UI Conditional Rendering**: Show/hide UI elements based on roles

```jsx
// Example conditional rendering
function SettingsButton() {
  const { userRole } = useAuth();
  
  if (['superadmin', 'admin'].includes(userRole)) {
    return <Button onClick={openSettings}>Settings</Button>;
  }
  
  return null;
}
```

### 4. API Access Control

1. **Middleware Validation**: Create Express/FastAPI middleware to validate role-based access

```python
# Example FastAPI middleware
def role_required(required_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            try:
                payload = verify_jwt(token.split(" ")[1])
                user_role = payload.get("role", "")
                
                if user_role not in required_roles:
                    raise HTTPException(
                        status_code=403, 
                        detail="Insufficient permissions"
                    )
                    
                return await func(request, *args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=401, detail=str(e))
        return wrapper
    return decorator

# Usage
@app.get("/admin/users")
@role_required(["superadmin", "admin"])
async def get_users():
    # Only accessible by superadmins and admins
    return {"users": get_all_users()}
```

## Supabase MCP Server Integration

To enhance the RBAC implementation, we'll integrate the Supabase MCP Server which will give us additional capabilities for managing authentication and roles.

### 1. Installation

```bash
# In your MCP servers directory
mkdir supabase-mcp
cd supabase-mcp
npm init -y
npm install @supabase-community/supabase-mcp
```

### 2. Configuration

Create a configuration file for the Supabase MCP server:

```javascript
// index.js
#!/usr/bin/env node
const { startServer } = require('@supabase-community/supabase-mcp');

// Start the MCP server
startServer({
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseKey: process.env.SUPABASE_SERVICE_ROLE_KEY
});
```

### 3. Update MCP Settings in Cline

```json
{
  "mcpServers": {
    "supabase": {
      "command": "node",
      "args": ["C:/Users/PhillMcGurk/OneDrive - Disaster Recovery/Documents/Cline/MCP/supabase-mcp/index.js"],
      "env": {
        "SUPABASE_URL": "https://rsooolwhapkkkwbmybdb.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Additional RBAC Features

### 1. Role Transition Workflows

Implement workflows for role transitions (e.g., promoting a Staff to Manager):

```sql
-- Example: Function to promote user
CREATE OR REPLACE FUNCTION promote_user(user_id UUID, new_role TEXT)
RETURNS VOID AS $$
DECLARE
  current_role TEXT;
BEGIN
  -- Get current role
  SELECT role INTO current_role FROM user_roles WHERE user_id = user_id LIMIT 1;
  
  -- Check if promotion is valid
  IF (current_role = 'staff' AND new_role = 'manager') OR
     (current_role = 'manager' AND new_role = 'admin') THEN
    
    -- Update role
    UPDATE user_roles SET role = new_role WHERE user_id = user_id;
    
    -- Log the change
    INSERT INTO role_change_logs (user_id, old_role, new_role, changed_by)
    VALUES (user_id, current_role, new_role, auth.uid());
  ELSE
    RAISE EXCEPTION 'Invalid role promotion from % to %', current_role, new_role;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 2. Temporary Access Grants

Implement temporary access elevation for specific tasks:

```sql
-- Example: Temporary permission grant table
CREATE TABLE temp_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  permission TEXT NOT NULL,
  granted_by UUID REFERENCES auth.users(id),
  expiry TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- Function to check temporary permissions
CREATE OR REPLACE FUNCTION has_temp_permission(permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM temp_permissions
    WHERE user_id = auth.uid()
    AND permission = permission
    AND expiry > now()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 3. Access Audit Logging

Implement comprehensive audit logging for security tracking:

```sql
-- Example: Audit log table
CREATE TABLE access_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  resource TEXT NOT NULL,
  action TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,
  successful BOOLEAN DEFAULT true,
  timestamp TIMESTAMP DEFAULT now()
);

-- Trigger function to log access
CREATE OR REPLACE FUNCTION log_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO access_logs (user_id, resource, action)
  VALUES (auth.uid(), TG_TABLE_NAME, TG_OP);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Implementation Timeline

1. **Week 1**: Set up Supabase authentication with basic role structure
2. **Week 2**: Implement PostgreSQL RLS policies and database schema
3. **Week 3**: Create API middleware and frontend route guards
4. **Week 4**: Integrate Supabase MCP Server and implement advanced features

## Testing Strategy

1. **Unit Tests**: Test individual access control functions
2. **Integration Tests**: Test complete authorization flows
3. **Security Audit**: Conduct a comprehensive security review
4. **User Acceptance Testing**: Verify with stakeholders that roles work as expected

---

This RBAC implementation will provide a solid foundation for the LocalLift CRM, ensuring that users can only access the features and data appropriate for their role while providing administrators with the flexibility to manage permissions effectively.
