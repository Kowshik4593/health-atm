-- =====================================================================
-- HealthATM Phase-3: Supabase Migration
-- 
-- New tables for:
-- 1. ai_chat_history — Stores AI agent conversation messages
-- 2. patient_episodes — Episodic memory for longitudinal tracking
--
-- References existing tables: profiles, patient_ct_scans
-- Run this in Supabase SQL Editor before using Phase-3 features.
-- =====================================================================


-- 1. AI Chat History Table
-- Stores conversation messages between patients and the AI assistant
CREATE TABLE IF NOT EXISTS public.ai_chat_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL,
    scan_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT ai_chat_history_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.profiles(id),
    CONSTRAINT ai_chat_history_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.patient_ct_scans(id)
);

-- Index for fast lookup by patient+scan
CREATE INDEX IF NOT EXISTS idx_ai_chat_patient_scan 
    ON public.ai_chat_history(patient_id, scan_id, created_at);

-- Index for patient-level queries
CREATE INDEX IF NOT EXISTS idx_ai_chat_patient 
    ON public.ai_chat_history(patient_id, created_at);


-- 2. Patient Episodes Table (Episodic Memory)
-- Stores time-indexed episodes for longitudinal patient tracking
CREATE TABLE IF NOT EXISTS public.patient_episodes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL,
    episode_type TEXT NOT NULL CHECK (episode_type IN (
        'scan_analysis',
        'chat_interaction',
        'report_generated',
        'doctor_consultation',
        'followup_scheduled'
    )),
    summary TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    scan_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT patient_episodes_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.profiles(id),
    CONSTRAINT patient_episodes_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.patient_ct_scans(id)
);

-- Index for patient timeline queries
CREATE INDEX IF NOT EXISTS idx_episodes_patient 
    ON public.patient_episodes(patient_id, created_at DESC);

-- Index for scan-specific episode queries
CREATE INDEX IF NOT EXISTS idx_episodes_scan 
    ON public.patient_episodes(scan_id) WHERE scan_id IS NOT NULL;

-- Index for episode type filtering
CREATE INDEX IF NOT EXISTS idx_episodes_type 
    ON public.patient_episodes(patient_id, episode_type);


-- Print success
DO $$ BEGIN RAISE NOTICE 'Phase-3 migration completed successfully!'; END $$;
