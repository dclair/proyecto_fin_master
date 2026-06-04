import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { Send, ArrowLeft } from 'lucide-react';

const MessageArea = ({ conversationId, onBack, currentUsername }) => {
  const { messages, sendMessage, setInitialMessages } = useWebSocket(conversationId);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);

  // Obtener historial al abrir la conversación
  useEffect(() => {
    setLoading(true);
    axios.get(`/api/chat/conversations/${conversationId}/messages/`)
      .then(response => {
        setInitialMessages(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error cargando mensajes:", error);
        setLoading(false);
      });
  }, [conversationId, setInitialMessages]);

  // Hacer scroll abajo cuando hay mensajes nuevos
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="message-area">
      <div className="message-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <div className="header-title">Chat #{conversationId}</div>
      </div>
      
      <div className="messages-list">
        {loading ? (
          <div className="loading">Cargando historial...</div>
        ) : (
          messages.map((msg, idx) => {
            // Verificar si el mensaje lo envié yo (si el username coincide)
            const isMe = msg.sender.username === currentUsername;
            
            return (
              <div key={msg.id || `temp-${idx}`} className={`message-bubble-wrapper ${isMe ? 'me' : 'them'}`}>
                <div className="message-bubble">
                  {!isMe && <div className="sender-name">{msg.sender.first_name || msg.sender.username}</div>}
                  <div className="message-content">{msg.content}</div>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="message-input-area" onSubmit={handleSend}>
        <input 
          type="text" 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Escribe un mensaje..."
          className="msg-input"
        />
        <button type="submit" className="send-btn" disabled={!inputValue.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};

export default MessageArea;
