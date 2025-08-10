import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-small py-micro body-s font-medium transition-colors duration-150',
  {
    variants: {
      variant: {
        default: 'bg-mist text-ocean-deep',
        success: 'bg-success/10 text-success border border-success/20',
        warning: 'bg-warning/10 text-warning border border-warning/20', 
        error: 'bg-error/10 text-error border border-error/20',
        info: 'bg-wave/10 text-atlantic border border-wave/20',
        neutral: 'bg-neutral/10 text-neutral border border-neutral/20',
      },
      size: {
        sm: 'px-small py-micro text-xs',
        md: 'px-small py-micro body-s', 
        lg: 'px-medium py-small body-m',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  children: React.ReactNode;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant, size, children, ...props }, ref) => {
    return (
      <div
        className={cn(badgeVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Badge.displayName = 'Badge';

export { Badge, badgeVariants };