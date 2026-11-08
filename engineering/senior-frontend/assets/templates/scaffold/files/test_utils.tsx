import { StrictMode, type ReactElement, type ReactNode } from 'react';
import { render, type RenderOptions } from '@testing-library/react';

function Providers({ children }: { children: ReactNode }) {
  // Add app-wide providers here (theme, query client, router) so tests render like the app.
  return <StrictMode>{children}</StrictMode>;
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) {
  return render(ui, { wrapper: Providers, ...options });
}

export * from '@testing-library/react';
