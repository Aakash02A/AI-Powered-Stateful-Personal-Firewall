import { useEffect, useRef, useState, useCallback } from 'react';
import toast from 'react-hot-toast';

export interface WebSocketPayload {
  topic: 'alert' | 'event';
  data: any;
}

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketPayload | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/stream';
    const apiKey = import.meta.env.VITE_API_KEY || 'default_dev_key';
    const urlWithAuth = `${wsUrl}?api_key=${apiKey}`;
    
    ws.current = new WebSocket(urlWithAuth);

    ws.current.onopen = () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      if (reconnectAttempts > 0) {
        toast.success('WebSocket Reconnected');
      }

      // Start Heartbeat
      heartbeatInterval.current = setInterval(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          ws.current.send('ping');
        }
      }, 15000); // Ping every 15 seconds
    };

    ws.current.onmessage = (event) => {
      if (event.data === 'pong') return; // Ignore heartbeat responses
      
      try {
        const msg: WebSocketPayload = JSON.parse(event.data);
        setLastMessage(msg);
        
        // Notify on high severity
        if (msg.topic === 'alert' && ['CRITICAL', 'HIGH'].includes(msg.data.severity)) {
           toast.error(`[${msg.data.severity}] ${msg.data.alert_type}: ${msg.data.src_ip}`);
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
      
      // Exponential backoff reconnect
      const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
      reconnectTimeout.current = setTimeout(() => {
        setReconnectAttempts(prev => prev + 1);
        connect();
      }, timeout);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error', error);
      ws.current?.close();
    };
  }, [reconnectAttempts]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (heartbeatInterval.current) clearInterval(heartbeatInterval.current);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  return { isConnected, lastMessage };
}
