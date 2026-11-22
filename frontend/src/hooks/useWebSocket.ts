import { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage, ChatUser, WebSocketMessagePayload } from '../types/chat.types';

export interface UseWebSocketReturn {
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  sendMessage: (text: string) => void;
  setInitialMessages: (initialMessages: ChatMessage[]) => void;
}

export const useWebSocket = (conversationId?: number | null): UseWebSocketReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!conversationId) return;

    // Determine protocol based on connection (ws vs wss)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // When using Vite proxy, we might need to point directly to the Django port for WS, 
    // or let it go relative if Nginx handles it. For now, we point to Django's default port 8000.
    const host = window.location.hostname;
    // En desarrollo, el backend está en 8000. En producción será el puerto actual.
    const port = import.meta.env.DEV ? '8000' : window.location.port;
    const portStr = port ? `:${port}` : '';
    
    const wsUrl = `${protocol}//${host}${portStr}/ws/chat/${conversationId}/`;

    console.log("Conectando WebSocket a:", wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
    };

    ws.current.onmessage = (event: MessageEvent<string>) => {
      try {
        const data: WebSocketMessagePayload = JSON.parse(event.data);
        console.log('Mensaje recibido:', data);
        
        if (data.action === 'delete') {
          setMessages((prev) => prev.filter(m => m.id !== data.message_id));
          return;
        }
        
        const msgId = data.message_id || data.id;
        if (!msgId) return;

        setMessages((prev) => {
          if (prev.some((m) => m.id === msgId)) {
            return prev.map((m) => m.id === msgId ? {
              ...m,
              content: data.message || data.content || m.content,
              attachment: data.attachment || m.attachment,
              attachment_name: data.attachment_name || m.attachment_name,
              attachment_type: data.attachment_type || m.attachment_type,
            } : m);
          }

          let senderUser: ChatUser;
          if (typeof data.sender === 'object' && data.sender !== null) {
            senderUser = data.sender as ChatUser;
          } else {
            senderUser = {
              id: 0,
              username: typeof data.sender === 'string' ? data.sender : 'Usuario',
            };
          }

          const newMsg: ChatMessage = {
            id: msgId,
            content: data.message || data.content || '',
            sender: senderUser,
            timestamp: data.timestamp || new Date().toISOString(),
            attachment: data.attachment,
            attachment_name: data.attachment_name,
            attachment_type: data.attachment_type,
          };

          return [...prev, newMsg];
        });
      } catch (err) {
        console.error('Error al parsear mensaje de WebSocket:', err);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket Disconnected');
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [conversationId]);

  const sendMessage = useCallback((text: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        message: text
      }));
    } else {
      console.error("No se pudo enviar, WebSocket no conectado");
    }
  }, []);

  // Metodo para inyectar mensajes históricos (obtenidos vía API)
  const setInitialMessages = useCallback((initialMessages: ChatMessage[]) => {
    setMessages(initialMessages);
  }, []);

  return { messages, setMessages, sendMessage, setInitialMessages };
};

export default useWebSocket;
