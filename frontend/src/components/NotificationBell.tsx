import React, { useState, useEffect } from 'react';
import { BellIcon } from '@heroicons/react/24/outline';

interface Notification {
  id: string;
  message: string;
  type: 'success' | 'warning' | 'error' | 'info';
  timestamp: string;
  read: boolean;
}

const NotificationBell: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  // Mock notifications - replace with actual API calls
  useEffect(() => {
    // This would be replaced with actual API calls
    const mockNotifications: Notification[] = [
      {
        id: '1',
        message: 'Project "Building Design" has been approved',
        type: 'success',
        timestamp: new Date().toISOString(),
        read: false,
      },
      {
        id: '2',
        message: 'New project submission requires review',
        type: 'info',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        read: false,
      },
    ];
    setNotifications(mockNotifications);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-success';
      case 'warning':
        return 'text-warning';
      case 'error':
        return 'text-error';
      default:
        return 'text-atlantic';
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2.5 text-neutral hover:text-ocean-deep hover:bg-mist/20 focus:outline-none focus:ring-2 focus:ring-atlantic/20 rounded-xl transition-all duration-200 ease-out group"
      >
        <BellIcon className="h-5 w-5 sm:h-6 sm:w-6 group-hover:scale-110 transition-transform duration-200" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
            <span className="relative inline-flex rounded-full h-5 w-5 bg-error items-center justify-center">
              <span className="text-white text-xs font-medium">{unreadCount > 9 ? '9+' : unreadCount}</span>
            </span>
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 top-full mt-2 w-72 sm:w-80 bg-white/95 backdrop-blur-md rounded-xl shadow-xl border border-mist/30 z-50 animate-slide-up">
          <div className="py-1">
            <div className="px-4 py-3 border-b border-mist/30">
              <h3 className="text-sm font-medium text-ocean-deep">
                Notifications {unreadCount > 0 && `(${unreadCount} unread)`}
              </h3>
            </div>
            
            {notifications.length === 0 ? (
              <div className="px-4 py-6 text-center text-sm text-neutral">
                No notifications
              </div>
            ) : (
              <div className="max-h-64 overflow-y-auto">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`px-4 py-3 border-b border-mist/20 last:border-b-0 ${
                      !notification.read ? 'bg-wave/5' : ''
                    }`}
                  >
                    <div className="flex items-start">
                      <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${getNotificationColor(notification.type).replace('text-', 'bg-')}`}></div>
                      <div className="ml-3 flex-1">
                        <p className="text-sm text-ocean-deep">
                          {notification.message}
                        </p>
                        <p className="text-xs text-neutral mt-1">
                          {new Date(notification.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            <div className="px-4 py-3 border-t border-mist/30">
              <button className="text-sm text-atlantic hover:text-ocean-deep transition-colors duration-150 min-h-[44px] flex items-center">
                View all notifications
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;