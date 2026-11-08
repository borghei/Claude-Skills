import { useForm, type FieldValues, type UseFormProps } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

/** react-hook-form wired to a Zod schema: values are typed from the schema. */
export function useZodForm<TInput extends FieldValues, TOutput extends FieldValues>(
  schema: z.ZodType<TOutput, TInput>,
  options?: Omit<UseFormProps<TInput, unknown, TOutput>, 'resolver'>
) {
  return useForm<TInput, unknown, TOutput>({
    ...options,
    resolver: zodResolver<TInput, unknown, TOutput>(schema),
  });
}

export const emailSchema = z.email('Enter a valid email address');

export const passwordSchema = z
  .string()
  .min(8, 'Use at least 8 characters')
  .max(128, 'Use at most 128 characters');
