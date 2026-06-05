import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { MessageCircle, X } from 'lucide-react';
import ConversationList from './components/ConversationList';
import MessageArea from './components/MessageArea';
import './ChatApp.css';

const ChatApp = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const panelRef = useRef(null);
  
  // Estados para el arrastre (Drag & Drop)
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  
  const currentUsername = window.DJANGO_USER || "";

  // Funciones de arrastre
  const handleMouseDown = (e) => {
    // Solo permitir arrastrar desde el header (click izquierdo)
    if (e.button !== 0) return;
    setIsDragging(true);
    dragStartPos.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - dragStartPos.current.x,
        y: e.clientY - dragStartPos.current.y
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  // Obtener mensajes no leídos periódicamente
  useEffect(() => {
    const fetchUnreadCount = () => {
      axios.get('/api/chat/unread_count/')
        .then(response => {
          setUnreadCount(response.data.unread_count || 0);
        })
        .catch(error => {
          console.error("Error obteniendo no leídos:", error);
        });
    };

    // Consultar inmediatamente
    fetchUnreadCount();

    // Luego cada 15 segundos
    const interval = setInterval(fetchUnreadCount, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (isOpen) {
      axios.get('/api/chat/conversations/')
        .then(response => {
          setConversations(response.data);
        })
        .catch(error => {
          console.error("Error cargando conversaciones:", error);
        });
    }
  }, [isOpen]);

  // Escuchar evento global para iniciar chat desde perfiles
  useEffect(() => {
    const handleOpenChat = (event) => {
      const { userId } = event.detail;
      setIsOpen(true);
      
      axios.post('/api/chat/conversations/create/', { user_id: userId }, {
        headers: {
          'X-CSRFToken': document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1]
        }
      })
      .then(response => {
        // Refrescar lista de conversaciones para incluir la nueva si no estaba
        axios.get('/api/chat/conversations/').then(res => setConversations(res.data));
        setActiveConversationId(response.data.id);
      })
      .catch(error => console.error("Error al iniciar chat:", error));
    };

    window.addEventListener('openChatWith', handleOpenChat);
    return () => window.removeEventListener('openChatWith', handleOpenChat);
  }, []);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target)) {
        // Asegurarse de no cerrar si el click fue en el botón de toggle
        if (!event.target.closest('#chat-toggle-link')) {
          setIsOpen(false);
        }
      }
    };
    
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleBackToList = () => {
    setActiveConversationId(null);
  };

  return (
    <>
      <a 
        id="chat-toggle-link"
        className="nav-link d-flex align-items-center text-nowrap position-relative" 
        href="#" 
        onClick={(e) => { e.preventDefault(); setIsOpen(!isOpen); }}
        title="Chat de la comunidad"
        style={{ cursor: 'pointer' }}
      >
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <MessageCircle size={20} className={isOpen ? 'text-hubs' : 'text-dark'} />
          {unreadCount > 0 && (
            <span 
              className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-white"
              style={{ fontSize: '0.55rem', padding: '0.2rem 0.35rem', marginTop: '2px', marginLeft: '-5px' }}
            >
              {unreadCount}
            </span>
          )}
        </div>
      </a>

      {isOpen && (
        <div 
          ref={panelRef}
          className="chat-panel shadow-lg"
          style={{
            position: 'absolute',
            top: '45px', // Justo debajo del navbar
            right: '-100px', // Centrado aprox respecto al icono
            width: '350px',
            height: '450px',
            backgroundColor: 'white',
            border: '1px solid #e5e5e5',
            borderRadius: '12px',
            zIndex: 9999,
            overflow: 'hidden',
            transform: `translate(${position.x}px, ${position.y}px)`,
            transition: isDragging ? 'none' : 'box-shadow 0.2s',
            boxShadow: isDragging ? '0 15px 30px rgba(0,0,0,0.2)' : ''
          }}
        >
          <div 
            className="chat-panel-header" 
            onMouseDown={handleMouseDown}
            style={{
              backgroundColor: '#0b5961', // Color "hubs"
              color: 'white',
              padding: '12px 15px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: isDragging ? 'grabbing' : 'grab',
              userSelect: 'none'
            }}
          >
            <span>Chat Terapeutas</span>
            <button 
              onClick={() => setIsOpen(false)}
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: 0 }}
            >
              <X size={18} />
            </button>
          </div>
          
          {activeConversationId ? (
            <MessageArea 
              conversationId={activeConversationId} 
              onBack={handleBackToList}
              currentUsername={currentUsername}
            />
          ) : (
            <ConversationList 
              conversations={conversations} 
              onSelect={(id) => setActiveConversationId(id)}
              activeId={activeConversationId}
            />
          )}
        </div>
      )}
    </>
  );
};

export default ChatApp;
