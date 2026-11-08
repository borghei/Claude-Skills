export function Footer() {
  return (
    <footer className="border-t py-6">
      <div className="container text-center text-sm text-muted-foreground">
        <p>&copy; {new Date().getFullYear()} My App. All rights reserved.</p>
      </div>
    </footer>
  );
}
