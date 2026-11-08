import { forwardRef, useId, type InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
}

// Works with react-hook-form:
// <FormField label="Email" {...register('email')} error={errors.email?.message} />
export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, hint, id, className, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const hintId = `${inputId}-hint`;
    const errorId = `${inputId}-error`;
    const describedBy = [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ');

    return (
      <div className="space-y-1">
        <label htmlFor={inputId} className="block text-sm font-medium">
          {label}
        </label>
        <input
          id={inputId}
          ref={ref}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy || undefined}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          {...props}
        />
        {hint && (
          <p id={hintId} className="text-sm text-muted-foreground">
            {hint}
          </p>
        )}
        {error && (
          <p id={errorId} role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';
