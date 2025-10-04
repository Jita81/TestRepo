/**
 * User presence indicator component
 */

import React from 'react';
import { Users } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';

export default function PresenceIndicator({ projectMembers = [] }) {
  const { onlineUsers } = useWebSocket();

  const onlineMembers = projectMembers.filter(member => 
    onlineUsers.includes(member.id)
  );

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
        <Users className="w-4 h-4" />
        <span className="text-sm">
          {onlineMembers.length} / {projectMembers.length} online
        </span>
      </div>

      <div className="flex -space-x-2">
        {onlineMembers.slice(0, 5).map((member) => (
          <div
            key={member.id}
            className="relative"
            title={member.username}
          >
            {member.avatarUrl ? (
              <img
                src={member.avatarUrl}
                alt={member.username}
                className="w-8 h-8 rounded-full border-2 border-white dark:border-gray-800"
              />
            ) : (
              <div className="w-8 h-8 rounded-full border-2 border-white dark:border-gray-800 bg-primary-500 flex items-center justify-center text-white text-xs font-medium">
                {member.username?.[0]?.toUpperCase() || '?'}
              </div>
            )}
            <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
          </div>
        ))}
        
        {onlineMembers.length > 5 && (
          <div className="w-8 h-8 rounded-full border-2 border-white dark:border-gray-800 bg-gray-300 dark:bg-gray-700 flex items-center justify-center text-xs font-medium">
            +{onlineMembers.length - 5}
          </div>
        )}
      </div>
    </div>
  );
}
