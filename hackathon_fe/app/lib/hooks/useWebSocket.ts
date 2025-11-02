/**
 * WebSocket Hook for AI Agent Chat
 * 
 * Kết nối với backend WebSocket server và quản lý real-time messaging
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export interface Message {
  type: 'text' | 'error' | 'system' | 'typing';
  content: string;
  metadata?: Record<string, any>;
  timestamp: string;
  role?: 'user' | 'assistant' | 'system';
}

export interface UseWebSocketOptions {
  url: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: Message) => void;
}

export function useWebSocket({
  url,
  autoConnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
  onOpen,
  onClose,
  onError,
  onMessage,
}: UseWebSocketOptions) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  // Parse message từ server
  const parseMessage = useCallback((data: string): Message => {
    try {
      const parsed = JSON.parse(data);
      return {
        type: parsed.type || 'text',
        content: parsed.content || data,
        metadata: parsed.metadata || {},
        timestamp: parsed.timestamp || new Date().toISOString(),
        role: 'assistant',
      };
    } catch {
      // Nếu không parse được JSON, coi như plain text
      return {
        type: 'text',
        content: data,
        metadata: {},
        timestamp: new Date().toISOString(),
        role: 'assistant',
      };
    }
  }, []);

  // Kết nối WebSocket
  const connect = useCallback(() => {
    // Kiểm tra nếu đang kết nối hoặc đã kết nối
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('Already connected');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('Already connecting');
      return;
    }

    if (connecting) {
      console.log('Connection in progress');
      return;
    }

    console.log('Initiating WebSocket connection...');
    setConnecting(true);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected, state:', ws.readyState);
        console.log('wsRef.current === ws?', wsRef.current === ws);
        setConnected(true);
        setConnecting(false);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        const message = parseMessage(event.data);
        
        // Handle typing indicator
        if (message.type === 'typing') {
          // Typing indicator sẽ được handle ở component level
          onMessage?.(message);
          return;
        }
        
        // Handle system messages (welcome, etc)
        if (message.type === 'system') {
          setMessages((prev) => [...prev, message]);
          onMessage?.(message);
          return;
        }
        
        // Handle error messages
        if (message.type === 'error') {
          setMessages((prev) => [...prev, message]);
          onMessage?.(message);
          return;
        }
        
        // Handle normal text messages
        setMessages((prev) => [...prev, message]);
        onMessage?.(message);
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        onError?.(error);
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setConnected(false);
        setConnecting(false);
        onClose?.();
        
        // Chỉ set wsRef null nếu đây là connection hiện tại
        if (wsRef.current === ws) {
          wsRef.current = null;
        }

        // Auto reconnect - CHỈ nếu chưa vượt quá giới hạn
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `🔄 Reconnecting in ${reconnectInterval}ms... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );
          
          // Clear timeout cũ nếu có
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          
          reconnectTimeoutRef.current = setTimeout(() => {
            // Kiểm tra lại trước khi reconnect
            if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
              connect();
            }
          }, reconnectInterval);
        } else {
          console.log('❌ Max reconnect attempts reached. Giving up.');
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnecting(false);
    }
  }, [url, connecting, reconnectInterval, maxReconnectAttempts, onOpen, onClose, onError, onMessage, parseMessage]);

  // Ngắt kết nối
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    reconnectAttemptsRef.current = maxReconnectAttempts; // Prevent auto reconnect
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, [maxReconnectAttempts]);

  // Gửi tin nhắn
  const sendMessage = useCallback((content: string, metadata?: Record<string, any>) => {
    const ws = wsRef.current;
    
    console.log('sendMessage called, ws state:', ws?.readyState);
    
    if (!ws) {
      console.error('WebSocket is not connected - ws is null');
      return false;
    }
    
    if (ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected - state:', ws.readyState);
      return false;
    }

    try {
      // Thêm tin nhắn user vào list
      const userMessage: Message = {
        type: 'text',
        content,
        metadata: metadata || {},
        timestamp: new Date().toISOString(),
        role: 'user',
      };
      setMessages((prev) => [...prev, userMessage]);

      // Gửi qua WebSocket (backend chỉ cần plain text hoặc JSON)
      console.log('Sending message:', content);
      ws.send(content);
      return true;
    } catch (error) {
      console.error('Failed to send message:', error);
      return false;
    }
  }, []); // Empty deps ok vì wsRef là ref (stable)

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Auto connect khi mount - CHỈ chạy 1 lần
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      reconnectAttemptsRef.current = maxReconnectAttempts; // Stop reconnect
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Chỉ chạy 1 lần khi mount

  return {
    messages,
    connected,
    connecting,
    connect,
    disconnect,
    sendMessage,
    clearMessages,
  };
}
