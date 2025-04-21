-- LocalLift CRM Database Schema for Role-Based Access Control
-- Migration: 20250419_rbac_schema
-- Description: Sets up the core tables for role-based access control and CRM functionality

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- RBAC Core Tables
-- ==========================================

-- User Roles Table
CREATE TABLE IF NOT EXISTS public.user_roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'staff', 'manager', 'admin', 'superadmin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- User Teams Table (for hierarchical team structure)
CREATE TABLE IF NOT EXISTS public.user_teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  manager_id UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id, manager_id)
);

-- Temporary Permissions Table
CREATE TABLE IF NOT EXISTS public.temp_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  permission TEXT NOT NULL,
  granted_by UUID REFERENCES auth.users(id) NOT NULL,
  expiry TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Role Change Logs
CREATE TABLE IF NOT EXISTS public.role_change_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  old_role TEXT NOT NULL,
  new_role TEXT NOT NULL,
  changed_by UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Activity Logs
CREATE TABLE IF NOT EXISTS public.activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,
  resource TEXT NOT NULL,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Access Logs
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

-- ==========================================
-- User Profile and Preferences Tables
-- ==========================================

-- User Profiles
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  phone TEXT,
  job_title TEXT,
  company TEXT,
  bio TEXT,
  last_login TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- User Preferences
CREATE TABLE IF NOT EXISTS public.user_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  theme TEXT DEFAULT 'light',
  dashboard_layout JSONB,
  notifications JSONB,
  language TEXT DEFAULT 'en',
  timezone TEXT DEFAULT 'UTC',
  date_format TEXT DEFAULT 'MM/DD/YYYY',
  time_format TEXT DEFAULT '12h',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- ==========================================
-- CRM Core Tables
-- ==========================================

-- Customers
CREATE TABLE IF NOT EXISTS public.customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  company TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'lead', 'prospect', 'churned')),
  assigned_to UUID REFERENCES auth.users(id),
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Customer Interactions
CREATE TABLE IF NOT EXISTS public.customer_interactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES public.customers(id) NOT NULL,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('email', 'call', 'meeting', 'note', 'other')),
  content TEXT,
  scheduled_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Customer Reviews
CREATE TABLE IF NOT EXISTS public.customer_reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  platform TEXT NOT NULL,
  author TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  content TEXT,
  responded BOOLEAN DEFAULT false,
  response TEXT,
  date DATE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Customer Inquiries
CREATE TABLE IF NOT EXISTS public.customer_inquiries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  subject TEXT,
  message TEXT NOT NULL,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'resolved', 'spam')),
  assigned_to UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Orders
CREATE TABLE IF NOT EXISTS public.orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES public.customers(id) NOT NULL,
  amount DECIMAL(10, 2) NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'cancelled', 'refunded')),
  date DATE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Website Visits
CREATE TABLE IF NOT EXISTS public.website_visits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source TEXT,
  count INTEGER DEFAULT 1,
  date DATE,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Customer Engagement
CREATE TABLE IF NOT EXISTS public.customer_engagement (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source TEXT NOT NULL,
  count INTEGER DEFAULT 1,
  day_of_week INTEGER CHECK (day_of_week >= 1 AND day_of_week <= 7),
  hour_of_day INTEGER CHECK (hour_of_day >= 0 AND hour_of_day <= 23),
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Reports
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  title TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('performance', 'engagement', 'customer', 'revenue', 'custom')),
  parameters JSONB,
  data JSONB,
  summary TEXT,
  file_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ==========================================
-- Helper Functions
-- ==========================================

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

-- Function to get a user by email
CREATE OR REPLACE FUNCTION public.get_user_by_email(email_to_find TEXT)
RETURNS JSONB AS $$
DECLARE
  user_data JSONB;
BEGIN
  SELECT json_build_object(
    'id', id,
    'email', email,
    'created_at', created_at
  )::JSONB INTO user_data
  FROM auth.users
  WHERE email = email_to_find;
  
  RETURN user_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add role claim to JWT token
CREATE OR REPLACE FUNCTION public.add_role_to_jwt()
RETURNS TRIGGER AS $$
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

-- Function to log user access
CREATE OR REPLACE FUNCTION public.log_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.access_logs (user_id, resource, action)
  VALUES (auth.uid(), TG_TABLE_NAME, TG_OP);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==========================================
-- Triggers
-- ==========================================

-- Add trigger for setting role in JWT token
DROP TRIGGER IF EXISTS add_role_to_jwt ON auth.tokens;
CREATE TRIGGER add_role_to_jwt
  BEFORE INSERT ON auth.tokens
  FOR EACH ROW
  EXECUTE PROCEDURE public.add_role_to_jwt();
  
-- Add triggers for logging access to sensitive tables
DROP TRIGGER IF EXISTS log_user_roles_access ON public.user_roles;
CREATE TRIGGER log_user_roles_access
  AFTER INSERT OR UPDATE OR DELETE ON public.user_roles
  FOR EACH ROW
  EXECUTE PROCEDURE public.log_access();
  
DROP TRIGGER IF EXISTS log_customers_access ON public.customers;
CREATE TRIGGER log_customers_access
  AFTER INSERT OR UPDATE OR DELETE ON public.customers
  FOR EACH ROW
  EXECUTE PROCEDURE public.log_access();

-- ==========================================
-- RLS Policies
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.temp_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_change_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_inquiries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.website_visits ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_engagement ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- User Roles Policies
CREATE POLICY view_own_role ON public.user_roles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY admin_manage_roles ON public.user_roles
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'superadmin')
    )
  );

-- User Teams Policies
CREATE POLICY view_own_team ON public.user_teams
  FOR SELECT USING (auth.uid() = user_id OR auth.uid() = manager_id);

CREATE POLICY manager_manage_team ON public.user_teams
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('manager', 'admin', 'superadmin')
    )
  );

-- User Profiles Policies
CREATE POLICY view_own_profile ON public.user_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY update_own_profile ON public.user_profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY admin_view_profiles ON public.user_profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'superadmin')
    )
  );

-- User Preferences Policies
CREATE POLICY view_own_preferences ON public.user_preferences
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY update_own_preferences ON public.user_preferences
  FOR UPDATE USING (auth.uid() = user_id);

-- Customers Policies
CREATE POLICY view_customers ON public.customers
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('staff', 'manager', 'admin', 'superadmin')
    )
  );

CREATE POLICY staff_create_customers ON public.customers
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('staff', 'manager', 'admin', 'superadmin')
    )
  );

CREATE POLICY staff_update_customers ON public.customers
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('staff', 'manager', 'admin', 'superadmin')
    )
  );

CREATE POLICY admin_delete_customers ON public.customers
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('admin', 'superadmin')
    )
  );

-- Reports Policies
CREATE POLICY view_reports ON public.reports
  FOR SELECT USING (
    auth.uid() = user_id OR
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('staff', 'manager', 'admin', 'superadmin')
    )
  );

CREATE POLICY create_reports ON public.reports
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.user_roles
      WHERE user_id = auth.uid() AND role IN ('staff', 'manager', 'admin', 'superadmin')
    )
  );

-- Add default superadmin user
-- Note: This requires a real user to exist in auth.users first
-- INSERT INTO public.user_roles (user_id, role)
-- VALUES ('replace-with-real-user-id', 'superadmin');

-- Add comments to tables for better documentation
COMMENT ON TABLE public.user_roles IS 'Stores user roles for RBAC';
COMMENT ON TABLE public.user_teams IS 'Defines manager-user relationships';
COMMENT ON TABLE public.temp_permissions IS 'Temporary permission grants';
COMMENT ON TABLE public.role_change_logs IS 'Audit logs for role changes';
COMMENT ON TABLE public.activity_logs IS 'Comprehensive logs of all system activities';
COMMENT ON TABLE public.access_logs IS 'Audit logs for resource access';
COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';
COMMENT ON TABLE public.user_preferences IS 'User-specific settings and preferences';
COMMENT ON TABLE public.customers IS 'Customer information for CRM';
COMMENT ON TABLE public.customer_interactions IS 'Records of customer interactions';
COMMENT ON TABLE public.customer_reviews IS 'Customer reviews from various platforms';
COMMENT ON TABLE public.customer_inquiries IS 'Customer inquiries and contact form submissions';
COMMENT ON TABLE public.orders IS 'Customer orders and transactions';
COMMENT ON TABLE public.website_visits IS 'Website traffic analytics';
COMMENT ON TABLE public.customer_engagement IS 'Customer engagement metrics';
COMMENT ON TABLE public.reports IS 'Generated business reports';
