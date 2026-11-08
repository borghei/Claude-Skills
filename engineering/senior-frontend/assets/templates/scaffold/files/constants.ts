export const APP_NAME = 'My App';
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  dashboard: '/dashboard',
} as const;

export const QUERY_KEYS = {
  user: ['user'],
  products: ['products'],
} as const;
