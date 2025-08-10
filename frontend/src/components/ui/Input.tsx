import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const inputVariants = cva(
  'w-full border bg-white px-4 py-3 text-base transition-all duration-150 ease-out focus:outline-none focus:ring-1 focus:ring-atlantic/20 placeholder:text-neutral disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        default: 'border-mist focus:border-atlantic',
        error: 'border-red-300 focus:border-red-500 focus:ring-red-500/20',
      },
      size: {
        sm: 'px-3 py-2 text-sm',
        md: 'px-4 py-3 text-base',
        lg: 'px-4 py-4 text-lg',
      },
      rounded: {
        md: 'rounded-lg',
        lg: 'rounded-xl',
        full: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      rounded: 'md',
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, size, rounded, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={inputVariants({ variant, size, rounded, className })}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = 'Input';

const Label = React.forwardRef<
  HTMLLabelElement,
  React.LabelHTMLAttributes<HTMLLabelElement>
>(({ className = '', ...props }, ref) => (
  <label
    ref={ref}
    className={`text-sm font-medium text-ocean-deep mb-2 block ${className}`}
    {...props}
  />
));
Label.displayName = 'Label';

export { Input, Label, inputVariants };