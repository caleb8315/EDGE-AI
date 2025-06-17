-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can view own agents" ON public.agents;
DROP POLICY IF EXISTS "Users can view own tasks" ON public.tasks;
DROP POLICY IF EXISTS "Users can view own companies" ON public.companies;

-- Updated RLS Policies that allow service role operations
CREATE POLICY "Users can manage own profile" ON public.users
    FOR ALL USING (
        auth.role() = 'service_role' OR 
        auth.uid()::text = id::text OR 
        auth.email() = email
    );

CREATE POLICY "Users can manage own agents" ON public.agents
    FOR ALL USING (
        auth.role() = 'service_role' OR
        auth.uid()::text IN (SELECT id::text FROM public.users WHERE id = agents.user_id)
    );

CREATE POLICY "Users can manage own tasks" ON public.tasks
    FOR ALL USING (
        auth.role() = 'service_role' OR
        auth.uid()::text IN (SELECT id::text FROM public.users WHERE id = tasks.user_id)
    );

CREATE POLICY "Users can manage own companies" ON public.companies
    FOR ALL USING (
        auth.role() = 'service_role' OR
        auth.uid()::text IN (SELECT id::text FROM public.users WHERE id = companies.user_id)
    ); 