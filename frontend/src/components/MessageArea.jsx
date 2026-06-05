import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { Send, ArrowLeft, Smile } from 'lucide-react';
import EmojiPicker from 'emoji-picker-react';

const MessageArea = ({ conversationId, onBack, currentUsername }) => {
  const { messages, sendMessage, setInitialMessages } = useWebSocket(conversationId);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const messagesEndRef = useRef(null);
  const emojiPickerRef = useRef(null);

  // Cerrar emoji picker al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target)) {
        setShowEmojiPicker(false);
      }
    };
    
    if (showEmojiPicker) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showEmojiPicker]);

  const onEmojiClick = (emojiObject) => {
    setInputValue(prevInput => prevInput + emojiObject.emoji);
  };

  // Marcar como leído
  const markAsRead = () => {
    // Para asegurar que Django CSRF se maneja correctamente, o usar el default de axios.
    // Asumimos que los endpoints en /api/ no requieren CSRF fuerte o axios lo toma de las cookies
    axios.post(`/api/chat/conversations/${conversationId}/read/`, {}, {
      headers: {
        'X-CSRFToken': document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1]
      }
    }).catch(e => console.error("Error al marcar como leído:", e));
  };

  // Obtener historial al abrir la conversación
  useEffect(() => {
    setLoading(true);
    axios.get(`/api/chat/conversations/${conversationId}/messages/`)
      .then(response => {
        setInitialMessages(response.data);
        setLoading(false);
        markAsRead(); // Marcar al cargar el historial
      })
      .catch(error => {
        console.error("Error cargando mensajes:", error);
        setLoading(false);
      });
  }, [conversationId, setInitialMessages]);

  // Hacer scroll abajo cuando hay mensajes nuevos y marcar como leído
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    // Si hay mensajes nuevos y tenemos la ventana abierta, marcamos como leído
    if (messages.length > 0) {
      markAsRead();
    }
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

      <form className="message-input-area" onSubmit={handleSend} style={{ position: 'relative' }}>
        {showEmojiPicker && (
          <div ref={emojiPickerRef} style={{ position: 'absolute', bottom: '60px', left: '10px', zIndex: 1000, boxShadow: '0 5px 15px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
            <EmojiPicker 
              onEmojiClick={onEmojiClick} 
              width={300} 
              height={350}
              searchPlaceholder="Buscar emoji..."
              lazyLoadEmojis={true}
            />
          </div>
        )}

        <button 
          type="button" 
          onClick={() => setShowEmojiPicker(val => !val)}
          style={{ background: 'none', border: 'none', color: showEmojiPicker ? '#0d6efd' : '#6c757d', cursor: 'pointer', padding: '0 8px 0 0', display: 'flex', alignItems: 'center' }}
          title="Insertar emoji"
        >
          <Smile size={24} />
        </button>

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
