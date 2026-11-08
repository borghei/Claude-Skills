import { useSyncExternalStore } from 'react';

// Client-side session state for a single-page app. It only remembers the token
// your server issued; it proves nothing on its own. Real authentication needs a
// server that checks credentials, issues the token and verifies it on every API call.
const STORAGE_KEY = 'auth-token';
const listeners = new Set<() => void>();

function readToken(): string | null {
  try {
    return window.sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function notify(): void {
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function getToken(): string | null {
  return readToken();
}

export function setToken(token: string): void {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, token);
  } catch {
    // Storage blocked (private mode, quota); the session lasts until reload.
  }
  notify();
}

export function clearToken(): void {
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // Nothing stored.
  }
  notify();
}

export function useAuth() {
  const token = useSyncExternalStore(subscribe, readToken, () => null);
  return { token, isAuthenticated: token !== null, signIn: setToken, signOut: clearToken };
}
