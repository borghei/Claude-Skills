// Signed session tokens for the cookie that proxy.ts checks.
// Web Crypto only (Node 20+, Edge runtime), no dependencies.
// Your login route checks the credentials against your user store, then calls
// createSessionToken() and sets SESSION_COOKIE with httpOnly, secure and sameSite: 'lax'.
export const SESSION_COOKIE = 'session';
const DEFAULT_MAX_AGE_SECONDS = 60 * 60 * 24 * 7;

export interface Session {
  userId: string;
  /** Expiry in seconds since the epoch. */
  expiresAt: number;
}

const encoder = new TextEncoder();

function toBase64Url(bytes: Uint8Array): string {
  let binary = '';
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function fromBase64Url(value: string) {
  const base64 = value.replace(/-/g, '+').replace(/_/g, '/');
  const binary = atob(base64 + '='.repeat((4 - (base64.length % 4)) % 4));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function hmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign', 'verify']
  );
}

/** Read the signing secret; fails loudly rather than signing with a weak or empty key. */
export function sessionSecret(): string {
  const secret = process.env.SESSION_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error('SESSION_SECRET must be set to at least 32 characters');
  }
  return secret;
}

export async function createSessionToken(
  userId: string,
  secret: string = sessionSecret(),
  maxAgeSeconds: number = DEFAULT_MAX_AGE_SECONDS
): Promise<string> {
  const session: Session = { userId, expiresAt: Math.floor(Date.now() / 1000) + maxAgeSeconds };
  const payload = toBase64Url(encoder.encode(JSON.stringify(session)));
  const signature = await crypto.subtle.sign('HMAC', await hmacKey(secret), encoder.encode(payload));
  return `${payload}.${toBase64Url(new Uint8Array(signature))}`;
}

/** Return the session when the token is authentic and unexpired, otherwise null. */
export async function verifySessionToken(
  token: string | undefined,
  secret: string = sessionSecret()
): Promise<Session | null> {
  const [payload, signature] = token?.split('.') ?? [];
  if (!payload || !signature) return null;
  try {
    const valid = await crypto.subtle.verify(
      'HMAC',
      await hmacKey(secret),
      fromBase64Url(signature),
      encoder.encode(payload)
    );
    if (!valid) return null;
    const session = JSON.parse(new TextDecoder().decode(fromBase64Url(payload))) as Session;
    return session.expiresAt > Date.now() / 1000 ? session : null;
  } catch {
    return null;
  }
}
