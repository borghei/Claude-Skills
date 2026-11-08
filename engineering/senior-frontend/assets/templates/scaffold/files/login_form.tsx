import { useState, type FormEvent } from 'react';
import { Button, Input } from '@/components/ui';

interface LoginFormProps {
  /** Endpoint that checks the credentials and starts the session. */
  action?: string;
  /** Called with the parsed response body after a successful sign-in. */
  onSuccess?: (data: unknown) => void;
}

export function LoginForm({ action = '/api/auth/login', onSuccess }: LoginFormProps) {
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setPending(true);
    setError(null);
    try {
      const response = await fetch(action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ email: form.get('email'), password: form.get('password') }),
      });
      if (!response.ok) {
        setError(response.status === 401 ? 'Email or password is incorrect.' : 'Sign-in failed. Try again.');
        return;
      }
      onSuccess?.(await response.json().catch(() => null));
    } catch {
      setError('Network error. Check your connection and try again.');
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1">
        <label htmlFor="login-email" className="block text-sm font-medium">
          Email
        </label>
        <Input id="login-email" name="email" type="email" autoComplete="email" required />
      </div>
      <div className="space-y-1">
        <label htmlFor="login-password" className="block text-sm font-medium">
          Password
        </label>
        <Input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button type="submit" disabled={pending} className="w-full">
        {pending ? 'Signing in...' : 'Sign in'}
      </Button>
    </form>
  );
}
