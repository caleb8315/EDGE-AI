-- Add auth_user_id column to users table
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS auth_user_id TEXT;

-- Add auth_user_id column to tasks table  
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS auth_user_id TEXT;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON public.users(auth_user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_auth_user_id ON public.tasks(auth_user_id);

-- Update RLS policies to use auth_user_id for better security
DROP POLICY IF EXISTS "Users can manage own profile" ON public.users;
DROP POLICY IF EXISTS "Users can manage own tasks" ON public.tasks;

CREATE POLICY "Users can manage own profile" ON public.users
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        auth.uid()::text = auth_user_id OR 
        auth.email() = email
    );

CREATE POLICY "Users can manage own tasks" ON public.tasks
    FOR ALL USING (
        auth.role() = 'service_role' OR
        auth.uid()::text = auth_user_id
    ); 