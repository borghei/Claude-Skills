import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2',
            'text-sm ring-offset-background file:border-0 file:bg-transparent',
            'file:text-sm file:font-medium placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-destructive">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input, type InputProps };
