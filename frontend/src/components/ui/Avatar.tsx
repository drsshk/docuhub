import React from 'react';
import { cn } from '../../lib/utils';
import { getInitials } from '../../lib/utils';

interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Avatar: React.FC<AvatarProps> = ({ 
  src, 
  alt, 
  name = '', 
  size = 'md', 
  className 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 body-s',
    lg: 'w-12 h-12 body-m',
    xl: 'w-16 h-16 body-l',
  };

  const initials = getInitials(name);

  if (src) {
    return (
      <img
        src={src}
        alt={alt || name}
        className={cn(
          'rounded-full object-cover bg-mist',
          sizeClasses[size],
          className
        )}
      />
    );
  }

  return (
    <div
      className={cn(
        'rounded-full bg-atlantic text-white flex items-center justify-center font-medium',
        sizeClasses[size],
        className
      )}
    >
      {initials}
    </div>
  );
};

export { Avatar };