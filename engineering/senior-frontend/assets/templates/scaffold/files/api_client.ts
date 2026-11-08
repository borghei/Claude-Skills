// Typed fetch wrapper with JSON bodies and a typed error; no dependencies.
export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, message: string, body: unknown = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

type Method = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

function parseBody(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export function createApiClient(baseUrl: string, defaultHeaders: Record<string, string> = {}) {
  async function request<T>(
    method: Method,
    path: string,
    body?: unknown,
    init: RequestInit = {}
  ): Promise<T> {
    const headers = new Headers(init.headers);
    for (const [name, value] of Object.entries(defaultHeaders)) {
      if (!headers.has(name)) headers.set(name, value);
    }
    if (!headers.has('Accept')) headers.set('Accept', 'application/json');
    if (body !== undefined && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${baseUrl}${path}`, {
      credentials: 'same-origin',
      ...init,
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const text = await response.text();
    const data = text ? parseBody(text) : null;
    if (!response.ok) {
      throw new ApiError(response.status, `${method} ${path} failed with ${response.status}`, data);
    }
    return data as T;
  }

  return {
    get: <T>(path: string, init?: RequestInit) => request<T>('GET', path, undefined, init),
    post: <T>(path: string, body?: unknown, init?: RequestInit) => request<T>('POST', path, body, init),
    put: <T>(path: string, body?: unknown, init?: RequestInit) => request<T>('PUT', path, body, init),
    patch: <T>(path: string, body?: unknown, init?: RequestInit) => request<T>('PATCH', path, body, init),
    delete: <T>(path: string, init?: RequestInit) => request<T>('DELETE', path, undefined, init),
  };
}

export const api = createApiClient('/api');
