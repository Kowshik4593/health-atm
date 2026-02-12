// frontend/middleware.ts

import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

// Public routes that don't require authentication
const publicRoutes = [
    '/',
    '/login',
    '/signup',
    '/reset-request',
    '/reset-verify',
    '/landing',
];

// Routes that require authentication but NOT profile completion
const authOnlyRoutes = [
    '/complete-profile',
];

export async function middleware(request: NextRequest) {
    // 1. Initialize Response
    // We create a response object that we can attach cookies to
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    });

    // 2. Create Supabase Server Client (handles cookies)
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll();
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value));
                    response = NextResponse.next({
                        request: {
                            headers: request.headers,
                        },
                    });
                    cookiesToSet.forEach(({ name, value, options }) =>
                        response.cookies.set(name, value, options)
                    );
                },
            },
        }
    );

    // 3. Refresh Session (Critical for Server Components)
    // This updates the auth cookie if it's expired
    const { data: { user } } = await supabase.auth.getUser();

    const pathname = request.nextUrl.pathname;

    // 4. Bypass static files and API routes
    if (
        pathname.startsWith('/_next') ||
        pathname.startsWith('/api') ||
        pathname.startsWith('/static') ||
        pathname.includes('.') // images, icons, etc.
    ) {
        return response;
    }

    // 5. Public Route Logic
    const isPublic = publicRoutes.some(route =>
        pathname === route || pathname.startsWith(`${route}/`)
    );

    if (isPublic) {
        // If logged in and trying to access Login/Signup, redirect to Dashboard
        if (user && (pathname === '/login' || pathname === '/signup' || pathname === '/')) {
            try {
                const { data: profile } = await supabase
                    .from('profiles')
                    .select('role')
                    .eq('id', user.id)
                    .single();

                if (profile?.role) {
                    return NextResponse.redirect(new URL(`/dashboard/${profile.role}`, request.url));
                }
                return NextResponse.redirect(new URL('/complete-profile', request.url));
            } catch (e) {
                // If fetching profile fails, just let them go to dashboard/patient as fallback
                return NextResponse.redirect(new URL('/dashboard/patient', request.url));
            }
        }
        return response;
    }

    // 6. Protected Route Logic
    if (!user) {
        // Not logged in -> Redirect to Login
        const redirectUrl = new URL('/login', request.url);
        redirectUrl.searchParams.set('redirect', pathname);
        return NextResponse.redirect(redirectUrl);
    }

    // 7. Profile & Role Check
    // We strictly enforce profile completion for all protected routes except the profile page itself
    if (!authOnlyRoutes.includes(pathname)) {
        try {
            const { data: profile, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', user.id)
                .single();

            // Check 1: Does profile exist?
            if (error || !profile) {
                return NextResponse.redirect(new URL('/complete-profile', request.url));
            }

            // Check 2: Is profile fully complete?
            // (Preserving your strict logic)
            const isProfileComplete =
                profile.full_name &&
                profile.phone &&
                profile.state &&
                profile.city &&
                profile.role;

            if (!isProfileComplete) {
                return NextResponse.redirect(new URL('/complete-profile', request.url));
            }

            // Check 3: Role-based Access Control for Dashboards
            // Prevent Patient from seeing Doctor Dashboard, etc.
            if (pathname.startsWith('/dashboard/')) {
                const requestedRole = pathname.split('/')[2]; // e.g. 'doctor' from /dashboard/doctor
                const userRole = profile.role;

                if (requestedRole && ['doctor', 'operator', 'patient'].includes(requestedRole)) {
                    if (requestedRole !== userRole) {
                        // User is in the wrong neighborhood -> Redirect to their own dashboard
                        return NextResponse.redirect(new URL(`/dashboard/${userRole}`, request.url));
                    }
                }
            }

            // Check 4: Redirect generic /dashboard to specific role
            if (pathname === '/dashboard') {
                return NextResponse.redirect(new URL(`/dashboard/${profile.role}`, request.url));
            }

        } catch (e) {
            console.error('Middleware Profile Check Error:', e);
            // Safety net: redirect to complete profile if something crashes
            return NextResponse.redirect(new URL('/complete-profile', request.url));
        }
    }

    return response;
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
};