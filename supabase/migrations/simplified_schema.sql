-- LocalLift CRM Simplified Database Schema
-- Modified to avoid auth schema dependencies

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- RBAC Core Tables - Without Foreign Keys
-- ==========================================

-- User Roles Table (without foreign key to auth.users)
CREATE TABLE IF NOT EXISTS public.user_roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'staff', 'manager', 'admin', 'superadmin')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- User Teams Table (without foreign keys)
CREATE TABLE IF NOT EXISTS public.user_teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
  manager_id UUID NOT NULL,  -- No foreign key reference
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id, manager_id)
);

-- Temporary Permissions Table (without foreign keys)
CREATE TABLE IF NOT EXISTS public.temp_permissions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
  permission TEXT NOT NULL,
  granted_by UUID NOT NULL,  -- No foreign key reference
  expiry TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Role Change Logs (without foreign keys)
CREATE TABLE IF NOT EXISTS public.role_change_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
  old_role TEXT NOT NULL,
  new_role TEXT NOT NULL,
  changed_by UUID NOT NULL,  -- No foreign key reference
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Activity Logs (without foreign keys)
CREATE TABLE IF NOT EXISTS public.activity_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID,  -- No foreign key reference
  action TEXT NOT NULL,
  resource TEXT NOT NULL,
  details JSONB,
  ip_address TEXT,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Access Logs (without foreign keys)
CREATE TABLE IF NOT EXISTS public.access_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID,  -- No foreign key reference
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

-- User Profiles (without foreign keys)
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
  phone TEXT,
  job_title TEXT,
  company TEXT,
  bio TEXT,
  last_login TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id)
);

-- User Preferences (without foreign keys)
CREATE TABLE IF NOT EXISTS public.user_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
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

-- Customers (without foreign keys)
CREATE TABLE IF NOT EXISTS public.customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  company TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'lead', 'prospect', 'churned')),
  assigned_to UUID,  -- No foreign key reference
  created_by UUID,  -- No foreign key reference
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Customer Interactions (with reference only to customers, not users)
CREATE TABLE IF NOT EXISTS public.customer_interactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  customer_id UUID REFERENCES public.customers(id) NOT NULL,
  user_id UUID NOT NULL,  -- No foreign key reference
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

-- Customer Inquiries (without foreign keys)
CREATE TABLE IF NOT EXISTS public.customer_inquiries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  subject TEXT,
  message TEXT NOT NULL,
  status TEXT DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'resolved', 'spam')),
  assigned_to UUID,  -- No foreign key reference
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

-- Orders (with reference only to customers)
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

-- Reports (without foreign keys)
CREATE TABLE IF NOT EXISTS public.reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL,  -- No foreign key reference
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
-- Helper Functions (Simplified)
-- ==========================================

-- Simplified function to check if a user has a specific role
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

-- Simplified function to get a user by email (without auth.users dependency)
CREATE OR REPLACE FUNCTION public.get_user_by_email(email_to_find TEXT)
RETURNS JSONB AS $$
DECLARE
  user_data JSONB;
BEGIN
  -- This function now returns null as we don't have auth.users
  -- You'll need to modify this to work with your actual user table
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log user access (simplified, no auth.uid dependency)
CREATE OR REPLACE FUNCTION public.log_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.access_logs (resource, action)
  VALUES (TG_TABLE_NAME, TG_OP);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==========================================
-- Triggers (Removed auth.tokens trigger)
-- ==========================================

-- REMOVED: Trigger for setting role in JWT token as auth.tokens doesn't exist

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
-- RLS Policies (Simplified, no auth.uid references)
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

-- Note: RLS policies removed as they depend on auth.uid()
-- You'll need to implement these based on your authentication system

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
