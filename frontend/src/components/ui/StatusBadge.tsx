import React from 'react';
import { Badge } from './Badge';
import { STATUS_COLORS, type StatusType } from '../../lib/constants';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentIcon,
  PaperAirplaneIcon 
} from '@heroicons/react/24/outline';

interface StatusBadgeProps {
  status: StatusType;
  showIcon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig = {
  pending: {
    label: 'Pending Review',
    variant: 'warning' as const,
    icon: ClockIcon,
  },
  approved: {
    label: 'Approved',
    variant: 'success' as const,
    icon: CheckCircleIcon,
  },
  rejected: {
    label: 'Rejected',
    variant: 'error' as const,
    icon: XCircleIcon,
  },
  submitted: {
    label: 'Submitted',
    variant: 'info' as const,
    icon: PaperAirplaneIcon,
  },
  draft: {
    label: 'Draft',
    variant: 'neutral' as const,
    icon: DocumentIcon,
  },
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  showIcon = true, 
  size = 'md' 
}) => {
  const config = statusConfig[status];
  const IconComponent = config.icon;

  return (
    <Badge variant={config.variant} size={size}>
      {showIcon && <IconComponent className="w-3 h-3 mr-micro" />}
      {config.label}
    </Badge>
  );
};

export { StatusBadge };