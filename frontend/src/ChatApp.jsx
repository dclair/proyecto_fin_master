import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import axios from 'axios';
import { MessageCircle, X } from 'lucide-react';
import ConversationList from './components/ConversationList';
import MessageArea from './components/MessageArea';
import GroupCreator from './components/GroupCreator';
import GroupExplorer from './components/GroupExplorer';
import UserExplorer from './components/UserExplorer';
import './ChatApp.css';

const ChatApp = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [isCreatingGroup, setIsCreatingGroup] = useState(false);
  const [isExploringGroups, setIsExploringGroups] = useState(false);
  const [isExploringUsers, setIsExploringUsers] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const panelRef = useRef(null);
  
  // Estados para el arrastre (Drag & Drop)
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  
  const currentUsername = window.DJANGO_USER || "";

  // Detectar cambios en pantalla para centrar o ajustar en móvil
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Funciones de arrastre
  const handleDragStart = (e) => {
    // Para ratón: click izquierdo
    if (e.type === 'mousedown' && e.button !== 0) return;
    
    // Evitar scroll en táctil al empezar a arrastrar
    if (e.type === 'touchstart' && e.cancelable) {
      // Opcional: e.preventDefault() podría bloquear el click de botones dentro, lo aplicamos al move
    }
    
    setIsDragging(true);
    
    const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
    const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
    
    dragStartPos.current = {
      x: clientX - position.x,
      y: clientY - position.y
    };
  };

  useEffect(() => {
    const handleDragMove = (e) => {
      if (!isDragging) return;
      
      // Prevenir scroll de la página en móvil al arrastrar el chat
      if (e.type === 'touchmove' && e.cancelable) {
        e.preventDefault();
      }

      const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
      const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;

      setPosition({
        x: clientX - dragStartPos.current.x,
        y: clientY - dragStartPos.current.y
      });
    };

    const handleDragEnd = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleDragMove, { passive: false });
      document.addEventListener('mouseup', handleDragEnd);
      document.addEventListener('touchmove', handleDragMove, { passive: false });
      document.addEventListener('touchend', handleDragEnd);
    }
    return () => {
      document.removeEventListener('mousemove', handleDragMove);
      document.removeEventListener('mouseup', handleDragEnd);
      document.removeEventListener('touchmove', handleDragMove);
      document.removeEventListener('touchend', handleDragEnd);
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
    let interval;
    const fetchConversations = () => {
      axios.get('/api/chat/conversations/')
        .then(response => {
          setConversations(response.data);
        })
        .catch(error => {
          console.error("Error cargando conversaciones:", error);
        });
    };

    if (isOpen) {
      fetchConversations();
      interval = setInterval(fetchConversations, 15000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
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

  // Se eliminó el cierre automático al hacer clic fuera para permitir que 
  // el usuario navegue o cierre el menú hamburguesa sin perder el chat.
  // El chat ahora solo se cierra con la "X" o volviendo a pulsar el botón del menú.

  const handleBackToList = () => {
    setActiveConversationId(null);
    setIsCreatingGroup(false);
    setIsExploringGroups(false);
    setIsExploringUsers(false);
  };

  const handleStartPrivateChat = (userId) => {
    const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    axios.post('/api/chat/conversations/create/', { user_id: userId }, {
      headers: { 'X-CSRFToken': token }
    })
    .then(response => {
      setConversations(prev => {
        const exists = prev.find(c => c.id === response.data.id);
        if (exists) return prev;
        return [response.data, ...prev];
      });
      setActiveConversationId(response.data.id);
      setIsExploringUsers(false);
    })
    .catch(error => console.error("Error al iniciar chat privado:", error));
  };

  const handleConversationDeleted = () => {
    setActiveConversationId(null);
    axios.get('/api/chat/conversations/')
      .then(response => setConversations(response.data))
      .catch(error => console.error("Error recargando conversaciones:", error));
  };

  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const conversationTitle = activeConversation ? 
    (activeConversation.is_group ? (activeConversation.name || "Chat Grupal") : activeConversation.participants.map(p => p.first_name || p.username).join(", ")) 
    : `Chat #${activeConversationId}`;
  const isGroup = activeConversation?.is_group || false;

  const sortedConversations = [...conversations].sort((a, b) => {
    if ((a.unread_count || 0) > 0 && (b.unread_count || 0) === 0) return -1;
    if ((b.unread_count || 0) > 0 && (a.unread_count || 0) === 0) return 1;
    const dateA = a.last_message ? new Date(a.last_message.timestamp) : new Date(a.created_at);
    const dateB = b.last_message ? new Date(b.last_message.timestamp) : new Date(b.created_at);
    return dateB - dateA;
  });

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
          <div 
            className="d-flex align-items-center justify-content-center text-white shadow-sm" 
            style={{ 
              backgroundColor: '#0b5961', 
              width: '28px', 
              height: '28px', 
              borderRadius: '50%',
              transition: 'transform 0.2s',
              transform: isOpen ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            <MessageCircle size={16} />
          </div>
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

      {isOpen && createPortal(
        <div 
          ref={panelRef}
          className="chat-panel shadow-lg"
          data-bs-theme="light"
          style={{
            position: 'fixed',
            top: isMobile ? '10vh' : 'auto',
            bottom: isMobile ? 'auto' : '80px',
            left: isMobile ? '5%' : 'auto',
            right: isMobile ? 'auto' : '20px',
            width: isMobile ? '90vw' : '350px',
            height: isMobile ? '70vh' : '450px',
            minWidth: isMobile ? '250px' : '300px',
            minHeight: isMobile ? '300px' : '400px',
            maxWidth: '100vw',
            maxHeight: '100vh',
            resize: 'both',
            backgroundColor: 'white',
            border: '1px solid #e5e5e5',
            borderRadius: '12px',
            zIndex: 99999, // Superar al navbar offcanvas
            overflow: 'hidden',
            transform: `translate(${position.x}px, ${position.y}px)`,
            transition: isDragging ? 'none' : 'box-shadow 0.2s',
            boxShadow: isDragging ? '0 15px 30px rgba(0,0,0,0.2)' : '0 10px 20px rgba(0,0,0,0.1)'
          }}
        >
          <div 
            className="chat-panel-header" 
            onMouseDown={handleDragStart}
            onTouchStart={handleDragStart}
            style={{
              backgroundColor: '#0b5961', // Color "hubs"
              color: 'white',
              padding: '12px 15px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: isDragging ? 'grabbing' : 'grab',
              userSelect: 'none',
              touchAction: 'none' // Evitar comportamiento nativo de pan/scroll en móviles
            }}
          >
            <span>Chat Terapeutas</span>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setIsOpen(false);
              }}
              onTouchEnd={(e) => {
                e.stopPropagation();
                e.preventDefault();
                setIsOpen(false);
              }}
              style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: '5px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            >
              <X size={18} />
            </button>
          </div>
          
          {isCreatingGroup ? (
            <GroupCreator 
              onBack={() => setIsCreatingGroup(false)}
              onGroupCreated={(id) => {
                setIsCreatingGroup(false);
                setActiveConversationId(id);
                axios.get('/api/chat/conversations/').then(res => setConversations(res.data));
              }}
            />
          ) : isExploringGroups ? (
            <GroupExplorer 
              onBack={() => setIsExploringGroups(false)}
            />
          ) : isExploringUsers ? (
            <UserExplorer
              onBack={() => setIsExploringUsers(false)}
              onStartChat={handleStartPrivateChat}
            />
          ) : activeConversationId ? (
            <MessageArea 
              conversationId={activeConversationId} 
              conversationTitle={conversationTitle}
              isGroup={isGroup}
              activeConversation={activeConversation}
              onBack={handleBackToList}
              onConversationDeleted={handleConversationDeleted}
              currentUsername={currentUsername}
            />
          ) : (
            <ConversationList 
              conversations={sortedConversations} 
              onSelect={(id) => setActiveConversationId(id)}
              activeId={activeConversationId}
              onCreateGroup={() => setIsCreatingGroup(true)}
              onExploreGroups={() => setIsExploringGroups(true)}
              onExploreUsers={() => setIsExploringUsers(true)}
            />
          )}
        </div>,
        document.body
      )}
    </>
  );
};

export default ChatApp;
