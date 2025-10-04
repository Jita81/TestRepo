/**
 * WebSocket connection status indicator
 */

import React from 'react';
import { Wifi, WifiOff, RefreshCw } from 'lucide-react';
import { useWebSocket } from '../contexts/WebSocketContext';

export default function ConnectionStatus() {
  const { isConnected, reconnectAttempts } = useWebSocket();

  if (isConnected) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm">
        <Wifi className="w-4 h-4" />
        <span>Connected</span>
      </div>
    );
  }

  if (reconnectAttempts > 0) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-sm">
        <RefreshCw className="w-4 h-4 animate-spin" />
        <span>Reconnecting... ({reconnectAttempts})</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-sm">
      <WifiOff className="w-4 h-4" />
      <span>Disconnected</span>
    </div>
  );
}
