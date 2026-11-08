import type { ReactNode } from 'react';
import { useAuth } from '@/lib/auth';

interface RequireAuthProps {
  children: ReactNode;
  /** Rendered when no session token is present. */
  fallback?: ReactNode;
}

// A UI gate only: it hides screens from signed-out users but protects no data.
// Anyone can edit client code, so the API must verify the token on every request.
export function RequireAuth({ children, fallback }: RequireAuthProps) {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <>
        {fallback ?? (
          <p className="p-8 text-center">
            Please{' '}
            <a className="underline" href="/login">
              sign in
            </a>{' '}
            to continue.
          </p>
        )}
      </>
    );
  }

  return <>{children}</>;
}
