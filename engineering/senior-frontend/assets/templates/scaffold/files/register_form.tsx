import { useState, type FormEvent } from 'react';
import { Button, Input } from '@/components/ui';

const MIN_PASSWORD_LENGTH = 8;

interface RegisterFormProps {
  /** Endpoint that creates the account. */
  action?: string;
  /** Called with the parsed response body after the account is created. */
  onSuccess?: (data: unknown) => void;
}

export function RegisterForm({ action = '/api/auth/register', onSuccess }: RegisterFormProps) {
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const password = String(form.get('password') ?? '');
    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(`Use at least ${MIN_PASSWORD_LENGTH} characters for the password.`);
      return;
    }
    if (password !== form.get('confirm')) {
      setError('The passwords do not match.');
      return;
    }
    setPending(true);
    setError(null);
    try {
      const response = await fetch(action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ name: form.get('name'), email: form.get('email'), password }),
      });
      if (!response.ok) {
        setError(
          response.status === 409
            ? 'An account with this email already exists.'
            : 'Could not create the account. Try again.'
        );
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
        <label htmlFor="register-name" className="block text-sm font-medium">
          Name
        </label>
        <Input id="register-name" name="name" autoComplete="name" required />
      </div>
      <div className="space-y-1">
        <label htmlFor="register-email" className="block text-sm font-medium">
          Email
        </label>
        <Input id="register-email" name="email" type="email" autoComplete="email" required />
      </div>
      <div className="space-y-1">
        <label htmlFor="register-password" className="block text-sm font-medium">
          Password
        </label>
        <Input
          id="register-password"
          name="password"
          type="password"
          autoComplete="new-password"
          minLength={MIN_PASSWORD_LENGTH}
          required
        />
      </div>
      <div className="space-y-1">
        <label htmlFor="register-confirm" className="block text-sm font-medium">
          Confirm password
        </label>
        <Input
          id="register-confirm"
          name="confirm"
          type="password"
          autoComplete="new-password"
          required
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}
      <Button type="submit" disabled={pending} className="w-full">
        {pending ? 'Creating account...' : 'Create account'}
      </Button>
    </form>
  );
}
