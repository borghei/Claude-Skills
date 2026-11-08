interface SidebarProps {
  children?: React.ReactNode;
}

export function Sidebar({ children }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-14 z-30 h-[calc(100vh-3.5rem)] w-64 border-r bg-background">
      <div className="p-4">{children}</div>
    </aside>
  );
}
