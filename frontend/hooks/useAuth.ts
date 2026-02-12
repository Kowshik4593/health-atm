// frontend/hooks/useAuth.ts

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import supabase from '@/lib/supabaseClient';
import { User } from '@/types';

// Define the exact shape of the profile from DB
interface Profile {
    id: string;
    full_name: string | null;
    dob: string | null;
    gender: string | null;
    phone: string | null;
    role: 'doctor' | 'operator' | 'patient';
    role_locked: boolean;
    // Doctor fields
    license_number?: string;
    hospital?: string;
    specialization?: string;
    // Operator fields
    organization?: string;
    center_location?: string;
    // Patient fields
    medical_history?: string;
    emergency_contact?: string;
}

interface AuthState {
    user: User | null;
    profile: Profile | null;
    loading: boolean;
    error: string | null;
    isProfileComplete: boolean;
}

export function useAuth() {
    const router = useRouter();
    const [state, setState] = useState<AuthState>({
        user: null,
        profile: null,
        loading: true,
        error: null,
        isProfileComplete: false,
    });

    // Helper to determine if a profile has all necessary fields
    const checkProfileComplete = useCallback((profile: Profile | null): boolean => {
        if (!profile) return false;

        // Base required fields for all roles
        const baseComplete = !!(
            profile.full_name &&
            profile.dob &&
            profile.gender &&
            profile.phone
        );

        if (!baseComplete) return false;

        // Role-specific required fields
        switch (profile.role) {
            case 'doctor':
                return !!(profile.license_number && profile.specialization);
            case 'operator':
                return !!(profile.organization);
            case 'patient':
                return true; // Base fields are enough for patient in Phase 1
            default:
                return baseComplete;
        }
    }, []);

    // Initial Auth Check
    useEffect(() => {
        checkUser();

        // Listen for auth changes (login, logout, token refresh)
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, session) => {
                if (event === 'SIGNED_OUT') {
                    setState({
                        user: null,
                        profile: null,
                        loading: false,
                        error: null,
                        isProfileComplete: false
                    });
                    return;
                }

                if (session?.user) {
                    await fetchUserProfile(session.user.id);
                } else {
                    // No session found
                    setState(prev => ({ ...prev, loading: false, user: null }));
                }
            }
        );

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    async function checkUser() {
        try {
            const { data: { session } } = await supabase.auth.getSession();

            if (session?.user) {
                await fetchUserProfile(session.user.id);
            } else {
                setState({
                    user: null,
                    profile: null,
                    loading: false,
                    error: null,
                    isProfileComplete: false
                });
            }
        } catch (error) {
            setState({
                user: null,
                profile: null,
                loading: false,
                error: 'Failed to check auth',
                isProfileComplete: false
            });
        }
    }

    async function fetchUserProfile(userId: string) {
        try {
            // 1. Try to fetch the profile
            const { data: profile, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            // 2. Handle "Profile Not Found" (New User) specifically
            // code 'PGRST116' means 0 rows returned, which is normal for a new signup
            if (error && error.code !== 'PGRST116') {
                throw error; // Real DB error
            }

            // 3. Get Auth User details (email)
            const { data: { user: authUser } } = await supabase.auth.getUser();

            // 4. Construct Safe User Object
            // If profile is missing, we default to 'patient' role so the app doesn't crash.
            // The isProfileComplete check will force them to the setup page anyway.
            const safeUser: User = {
                id: userId,
                email: authUser?.email || '',
                role: profile?.role || 'patient', // Default role for new users
                full_name: profile?.full_name || undefined,
            };

            const isComplete = checkProfileComplete(profile);

            setState({
                user: safeUser,
                profile: profile || null,
                loading: false,
                error: null,
                isProfileComplete: isComplete,
            });

        } catch (error) {
            console.error('Profile fetch error:', error);
            // Critical: If we crash here, allow retry but stop loading
            setState({
                user: null,
                profile: null,
                loading: false,
                error: 'Failed to fetch profile',
                isProfileComplete: false
            });
        }
    }

    async function signOut() {
        await supabase.auth.signOut();
        setState({
            user: null,
            profile: null,
            loading: false,
            error: null,
            isProfileComplete: false
        });
        router.push('/login');
    }

    function redirectToDashboard() {
        if (!state.user) {
            router.push('/login');
            return;
        }

        if (!state.isProfileComplete) {
            router.push('/complete-profile');
            return;
        }

        router.push(`/dashboard/${state.user.role}`);
    }

    // --- Role Helpers ---

    function canUpload(): boolean {
        const role = state.user?.role;
        return role === 'doctor' || role === 'operator' || role === 'patient';
    }

    function canViewAllPatients(): boolean {
        const role = state.user?.role;
        return role === 'doctor' || role === 'operator';
    }

    function canAcceptCases(): boolean {
        return state.user?.role === 'doctor';
    }

    function canCreatePatient(): boolean {
        return state.user?.role === 'operator';
    }

    function getDashboardPath(): string {
        if (!state.user) return '/login';
        if (!state.isProfileComplete) return '/complete-profile';
        return `/dashboard/${state.user.role}`;
    }

    return {
        ...state,
        signOut,
        redirectToDashboard,
        canUpload,
        canViewAllPatients,
        canAcceptCases,
        canCreatePatient,
        getDashboardPath,
        refetch: checkUser,
    };
}