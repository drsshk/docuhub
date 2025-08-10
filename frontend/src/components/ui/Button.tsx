import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center font-medium transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-atlantic/20 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        primary: 'bg-atlantic text-white hover:bg-ocean-deep hover:-translate-y-px shadow-sm hover:shadow-md',
        secondary: 'bg-transparent border border-coastal text-coastal hover:bg-coastal hover:text-white',
        minimal: 'text-atlantic hover:text-ocean-deep',
        destructive: 'bg-red-600 text-white hover:bg-red-700',
      },
      size: {
        sm: 'px-3 py-2 text-sm min-h-[36px]',
        md: 'px-4 py-3 sm:px-6 sm:py-3 text-sm sm:text-base min-h-[44px] sm:min-h-[48px]',
        lg: 'px-6 py-3 sm:px-8 sm:py-4 text-base sm:text-lg min-h-[48px] sm:min-h-[52px]',
      },
      rounded: {
        md: 'rounded-lg',
        lg: 'rounded-xl',
        full: 'rounded-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      rounded: 'md',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, rounded, children, loading, disabled, ...props }, ref) => {
    return (
      <button
        className={buttonVariants({ variant, size, rounded, className })}
        disabled={disabled || loading}
        ref={ref}
        {...props}
      >
        {loading ? (
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent mr-2" />
            Loading...
          </div>
        ) : (
          children
        )}
      </button>
    );
  }
);
Button.displayName = 'Button';

export { Button, buttonVariants };