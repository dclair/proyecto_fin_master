import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (conversationId) => {
  const [messages, setMessages] = useState([]);
  const ws = useRef(null);

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

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Mensaje recibido:', data);
      
      if (data.action === 'delete') {
        setMessages((prev) => prev.filter(m => m.id !== data.message_id));
        return;
      }
      
      setMessages((prev) => [...prev, {
        id: data.message_id || data.id,
        content: data.message || data.content,
        sender: data.sender?.username ? data.sender : { username: data.sender }, 
        timestamp: data.timestamp,
        attachment: data.attachment,
        attachment_type: data.attachment_type
      }]);
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

  const sendMessage = useCallback((text) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        message: text
      }));
    } else {
      console.error("No se pudo enviar, WebSocket no conectado");
    }
  }, []);

  // Metodo para inyectar mensajes históricos (obtenidos vía API)
  const setInitialMessages = useCallback((initialMessages) => {
    setMessages(initialMessages);
  }, []);

  return { messages, sendMessage, setInitialMessages };
};
