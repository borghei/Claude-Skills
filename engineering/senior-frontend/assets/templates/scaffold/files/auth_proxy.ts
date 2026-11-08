import { NextResponse, type NextRequest } from 'next/server';

// Next 16 proxy (formerly middleware): runs before matched routes.
// Keep it to cheap checks such as redirects; do real authorization in the route itself.
export function proxy(request: NextRequest) {
  const session = request.cookies.get('session')?.value;
  if (!session) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
};
