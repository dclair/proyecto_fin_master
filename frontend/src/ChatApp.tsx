import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { MessageCircle, X } from 'lucide-react';
import ConversationList from './components/ConversationList';
import MessageArea from './components/MessageArea';
import GroupCreator from './components/GroupCreator';
import GroupExplorer from './components/GroupExplorer';
import UserExplorer from './components/UserExplorer';
import chatService from './api/chat.service';
import { Conversation } from './types/chat.types';
import { useHostTheme } from './hooks/useHostTheme';
import './ChatApp.css';

/**
 * ChatApp Main Shell
 * Architecture: Clean & decoupled with centralized ChatService
 */
export const ChatApp: React.FC = () => {
  const hostTheme = useHostTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [isCreatingGroup, setIsCreatingGroup] = useState(false);
  const [isExploringGroups, setIsExploringGroups] = useState(false);
  const [isExploringUsers, setIsExploringUsers] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const panelRef = useRef<HTMLDivElement | null>(null);

  // Estados para el arrastre (Drag & Drop)
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });

  const currentUsername = window.DJANGO_USER || '';

  // Detectar cambios en pantalla para centrar o ajustar en móvil
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Funciones de arrastre
  const handleDragStart = (e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => {
    if ('button' in e && e.button !== 0) return;
    setIsDragging(true);

    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

    dragStartPos.current = {
      x: clientX - position.x,
      y: clientY - position.y,
    };
  };

  useEffect(() => {
    const handleDragMove = (e: MouseEvent | TouchEvent) => {
      if (!isDragging) return;
      if ('cancelable' in e && e.cancelable && 'touches' in e) {
        e.preventDefault();
      }

      const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
      const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;

      setPosition({
        x: clientX - dragStartPos.current.x,
        y: clientY - dragStartPos.current.y,
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

  // Cargar contador de no leídos de forma inteligente
  const refreshUnreadCount = useCallback(() => {
    chatService
      .getUnreadCount()
      .then((count) => setUnreadCount(count))
      .catch((err) => console.warn('[ChatApp]: Error al obtener no leídos:', err));
  }, []);

  // Cargar lista de conversaciones
  const refreshConversations = useCallback(() => {
    chatService
      .getConversations()
      .then((data) => setConversations(data))
      .catch((err) => console.warn('[ChatApp]: Error cargando conversaciones:', err));
  }, []);

  // Polling inteligente: sincronizar inmediatamente y al recuperar el foco
  useEffect(() => {
    refreshUnreadCount();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        refreshUnreadCount();
        if (isOpen) refreshConversations();
      }
    };

    window.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleVisibilityChange);

    // Intervalo de respaldo relajado (30s) solo si la pestaña está activa
    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        refreshUnreadCount();
      }
    }, 30000);

    return () => {
      window.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleVisibilityChange);
      clearInterval(timer);
    };
  }, [refreshUnreadCount, refreshConversations, isOpen]);

  // Cargar conversaciones al abrir el panel
  useEffect(() => {
    if (!isOpen) return;

    refreshConversations();

    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') {
        refreshConversations();
      }
    }, 30000);

    return () => clearInterval(timer);
  }, [isOpen, refreshConversations]);

  // Escuchar evento global para iniciar chat desde perfiles
  useEffect(() => {
    const handleOpenChat = (event: Event) => {
      const customEvent = event as CustomEvent<{ userId: number }>;
      const { userId } = customEvent.detail;
      setIsOpen(true);

      chatService
        .createPrivateConversation(userId)
        .then((conv) => {
          refreshConversations();
          setActiveConversationId(conv.id);
        })
        .catch((err) => console.error('[ChatApp]: Error al iniciar chat:', err));
    };

    window.addEventListener('openChatWith', handleOpenChat);
    return () => window.removeEventListener('openChatWith', handleOpenChat);
  }, [refreshConversations]);

  const handleBackToList = () => {
    setActiveConversationId(null);
    setIsCreatingGroup(false);
    setIsExploringGroups(false);
    setIsExploringUsers(false);
    refreshConversations();
    refreshUnreadCount();
  };

  const handleStartPrivateChat = async (userId: number) => {
    try {
      const conv = await chatService.createPrivateConversation(userId);
      setConversations((prev) => {
        const exists = prev.find((c) => c.id === conv.id);
        if (exists) return prev;
        return [conv, ...prev];
      });
      setActiveConversationId(conv.id);
      setIsExploringUsers(false);
    } catch (err) {
      console.error('[ChatApp]: Error al iniciar chat privado:', err);
    }
  };

  const handleConversationDeleted = () => {
    setActiveConversationId(null);
    refreshConversations();
    refreshUnreadCount();
  };

  const activeConversation = conversations.find((c) => c.id === activeConversationId);
  const conversationTitle = activeConversation
    ? activeConversation.is_group
      ? activeConversation.name || 'Chat Grupal'
      : activeConversation.participants
          .map((p) => p.first_name || p.username)
          .join(', ')
    : `Chat #${activeConversationId}`;
  const isGroup = activeConversation?.is_group || false;

  const sortedConversations = [...conversations].sort((a, b) => {
    if ((a.unread_count || 0) > 0 && (b.unread_count || 0) === 0) return -1;
    if ((b.unread_count || 0) > 0 && (a.unread_count || 0) === 0) return 1;
    const dateA = a.last_message ? new Date(a.last_message.timestamp).getTime() : (a.created_at ? new Date(a.created_at).getTime() : 0);
    const dateB = b.last_message ? new Date(b.last_message.timestamp).getTime() : (b.created_at ? new Date(b.created_at).getTime() : 0);
    return dateB - dateA;
  });

  return (
    <>
      <a
        id="chat-toggle-link"
        className="nav-link px-2 d-flex align-items-center text-nowrap position-relative"
        href="#"
        onClick={(e) => {
          e.preventDefault();
          setIsOpen(!isOpen);
        }}
        title="Chat de la comunidad"
        style={{ cursor: 'pointer' }}
      >
        <span className="me-2 fw-medium">Chat</span>
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <div
            className="d-flex align-items-center justify-content-center text-white shadow-sm"
            style={{
              backgroundColor: 'var(--hubs-primary, #0b5961)',
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              transition: 'transform 0.2s',
              transform: isOpen ? 'scale(1.05)' : 'scale(1)',
            }}
          >
            <MessageCircle size={16} />
          </div>
          {unreadCount > 0 && (
            <span
              className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-light"
              style={{
                fontSize: '0.55rem',
                padding: '0.2rem 0.35rem',
                marginTop: '2px',
                marginLeft: '-5px',
              }}
            >
              {unreadCount}
            </span>
          )}
        </div>
      </a>

      {isOpen &&
        createPortal(
          <div
            ref={panelRef}
            className="chat-panel shadow-lg"
            data-bs-theme={hostTheme}
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
              backgroundColor: 'var(--bs-card-bg)',
              color: 'var(--bs-body-color)',
              border: '1px solid var(--bs-border-color)',
              borderRadius: '12px',
              zIndex: 99999,
              overflow: 'hidden',
              transform: `translate(${position.x}px, ${position.y}px)`,
              transition: isDragging ? 'none' : 'box-shadow 0.2s',
              boxShadow: isDragging
                ? '0 15px 30px rgba(0,0,0,0.3)'
                : '0 10px 20px rgba(0,0,0,0.15)',
            }}
          >
            <div
              className="chat-panel-header"
              onMouseDown={handleDragStart}
              onTouchStart={handleDragStart}
              style={{
                backgroundColor: 'var(--hubs-primary, #0b5961)',
                color: '#ffffff',
                padding: '12px 15px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: isDragging ? 'grabbing' : 'grab',
                userSelect: 'none',
                touchAction: 'none',
              }}
            >
              <span>Chat Terapeutas</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsOpen(false);
                }}
                onTouchEnd={(e) => {
                  e.stopPropagation();
                  e.preventDefault();
                  setIsOpen(false);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  padding: '5px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
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
                  refreshConversations();
                }}
              />
            ) : isExploringGroups ? (
              <GroupExplorer onBack={() => setIsExploringGroups(false)} />
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
