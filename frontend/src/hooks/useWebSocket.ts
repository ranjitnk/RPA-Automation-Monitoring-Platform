import { useEffect, useState, useCallback } from 'react';

interface WebSocketMessage<T = unknown> {
  type: string;
  data: T;
  timestamp: number;
}

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onError,
  reconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = url.startsWith('ws') ? url : `${protocol}//${window.location.host}${url}`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        setIsConnected(true);
        console.log(`WebSocket connected to ${wsUrl}`);
      };

      websocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      websocket.onclose = () => {
        setIsConnected(false);
        if (reconnect) {
          setTimeout(connect, reconnectInterval);
        }
      };

      setWs(websocket);
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [url, onMessage, onError, reconnect, reconnectInterval]);

  useEffect(() => {
    connect();
    return () => {
      ws?.close();
    };
  }, [connect, ws]);

  const send = useCallback(
    (message: WebSocketMessage) => {
      if (ws && isConnected) {
        ws.send(JSON.stringify(message));
      }
    },
    [ws, isConnected]
  );

  return { isConnected, send };
};
