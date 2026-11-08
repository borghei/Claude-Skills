import Link from 'next/link';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-14 items-center">
        <Link href="/" className="font-bold">
          Logo
        </Link>
        <nav className="ml-auto flex gap-4">
          <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground">
            About
          </Link>
        </nav>
      </div>
    </header>
  );
}
