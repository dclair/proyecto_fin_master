import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useWebSocket } from '../hooks/useWebSocket';
import { Send, ArrowLeft, Smile, UserPlus, Check, UserCheck, Trash2 } from 'lucide-react';
import EmojiPicker from 'emoji-picker-react';

const MessageArea = ({ conversationId, conversationTitle, isGroup, activeConversation, onBack, onConversationDeleted, currentUsername }) => {
  const { messages, sendMessage, setInitialMessages } = useWebSocket(conversationId);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  
  // States for adding members
  const [showAddMember, setShowAddMember] = useState(false);
  const [usersToAdd, setUsersToAdd] = useState([]);
  const [selectedUsersToAdd, setSelectedUsersToAdd] = useState([]);
  const [addingUsers, setAddingUsers] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  
  // States for pending requests
  const [pendingRequests, setPendingRequests] = useState([]);
  const [showPending, setShowPending] = useState(false);

  const messagesEndRef = useRef(null);
  const emojiPickerRef = useRef(null);
  const addMemberRef = useRef(null);
  const pendingRef = useRef(null);

  const me = activeConversation?.participants?.find(p => p.username === currentUsername);
  const isAdmin = isGroup && me && activeConversation.admin === me.id;

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

  // Cerrar add member al hacer clic fuera
  useEffect(() => {
    const handleClickOutsideAdd = (event) => {
      if (addMemberRef.current && !addMemberRef.current.contains(event.target)) {
        setShowAddMember(false);
        setUserSearchQuery('');
      }
    };
    
    if (showAddMember) {
      document.addEventListener('mousedown', handleClickOutsideAdd);
      // Fetch users when opened
      axios.get('/api/chat/users/')
        .then(res => setUsersToAdd(res.data))
        .catch(err => console.error("Error loading users:", err));
    }
    return () => document.removeEventListener('mousedown', handleClickOutsideAdd);
  }, [showAddMember]);

  // Fetch pending requests for admin
  useEffect(() => {
    if (isAdmin) {
      axios.get('/api/chat/groups/join_requests/')
        .then(res => {
          setPendingRequests(res.data.filter(r => r.conversation === conversationId));
        })
        .catch(console.error);
    }
  }, [isAdmin, conversationId, showPending]);

  // Cerrar panel de solicitudes al hacer clic fuera
  useEffect(() => {
    const handleClickOutsidePending = (event) => {
      if (pendingRef.current && !pendingRef.current.contains(event.target)) {
        setShowPending(false);
      }
    };
    if (showPending) {
      document.addEventListener('mousedown', handleClickOutsidePending);
    }
    return () => document.removeEventListener('mousedown', handleClickOutsidePending);
  }, [showPending]);

  const handleAddUsers = () => {
    if (selectedUsersToAdd.length === 0) return;
    setAddingUsers(true);
    const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    
    axios.post(`/api/chat/groups/${conversationId}/add_users/`, {
      user_ids: selectedUsersToAdd
    }, {
      headers: { 'X-CSRFToken': token }
    })
    .then(() => {
      setShowAddMember(false);
      setSelectedUsersToAdd([]);
      setAddingUsers(false);
      // Opcional: mostrar una notificación de éxito o enviar un mensaje automático
    })
    .catch(err => {
      console.error("Error adding users", err);
      setAddingUsers(false);
    });
  };

  const handleManageRequest = (requestId, action) => {
    const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    axios.post(`/api/chat/groups/join_requests/${requestId}/manage/`, { action }, { headers: { 'X-CSRFToken': token }})
      .then(() => {
        setPendingRequests(prev => prev.filter(r => r.id !== requestId));
      })
      .catch(console.error);
  };

  const handleDeleteConversation = () => {
    if (window.confirm("¿Estás seguro de que quieres eliminar este chat permanentemente? Esta acción no se puede deshacer y borrará el chat para todos.")) {
      const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
      axios.delete(`/api/chat/conversations/${conversationId}/delete/`, {
        headers: { 'X-CSRFToken': token }
      })
      .then(() => {
        if (onConversationDeleted) onConversationDeleted();
        else onBack();
      })
      .catch(err => {
        console.error("Error al eliminar conversación:", err);
        alert("No tienes permiso para eliminar este chat o hubo un error.");
      });
    }
  };

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
      <div className="message-header" style={{ position: 'relative' }}>
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <div className="header-title text-truncate" style={{maxWidth: '220px'}}>
          {conversationTitle || `Chat #${conversationId}`}
        </div>
        
        <div className="d-flex ms-auto gap-2">
          {(!isGroup || isAdmin) && (
            <button 
              className="btn btn-sm btn-link text-danger p-0"
              onClick={handleDeleteConversation}
              title="Eliminar chat"
            >
              <Trash2 size={18} />
            </button>
          )}

          {isAdmin && (
            <>
              {pendingRequests.length > 0 && (
                <button 
                  className="btn btn-sm btn-link text-warning p-0 position-relative"
                  onClick={() => setShowPending(!showPending)}
                  title="Solicitudes de acceso"
                >
                  <UserCheck size={18} />
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style={{fontSize: '0.5rem', padding: '0.15rem 0.25rem'}}>
                    {pendingRequests.length}
                  </span>
                </button>
              )}
              <button 
                className="btn btn-sm btn-link text-dark p-0"
                onClick={() => setShowAddMember(!showAddMember)}
                title="Añadir participante"
              >
                <UserPlus size={18} />
              </button>
            </>
          )}
        </div>

        {showPending && (
          <div ref={pendingRef} className="position-absolute shadow rounded p-2" style={{ top: '100%', right: '10px', width: '250px', zIndex: 1000, border: '1px solid #ccc', backgroundColor: 'white' }}>
            <div className="text-dark fw-bold mb-2" style={{fontSize: '0.85rem'}}>Solicitudes Pendientes</div>
            <div className="list-group list-group-flush mb-2" style={{maxHeight: '200px', overflowY: 'auto'}}>
              {pendingRequests.map(r => (
                <div key={r.id} className="list-group-item py-2 px-2 d-flex flex-column border-bottom">
                  <div className="d-flex align-items-center mb-1">
                    <img src={r.user.profile_picture_url} alt="" className="rounded-circle me-2" style={{width: '20px', height: '20px', objectFit: 'cover'}} />
                    <span className="text-truncate text-dark fw-bold" style={{fontSize: '0.8rem'}}>{r.user.first_name || r.user.username}</span>
                  </div>
                  <div className="d-flex gap-1 mt-1">
                    <button className="btn btn-sm btn-success py-0 flex-grow-1" style={{fontSize: '0.75rem'}} onClick={() => handleManageRequest(r.id, 'accept')}>Aceptar</button>
                    <button className="btn btn-sm btn-outline-danger py-0 flex-grow-1" style={{fontSize: '0.75rem'}} onClick={() => handleManageRequest(r.id, 'reject')}>Rechazar</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {showAddMember && (
          <div ref={addMemberRef} className="position-absolute shadow rounded p-2" style={{ top: '100%', right: '10px', width: '250px', zIndex: 1000, border: '1px solid #ccc', backgroundColor: 'white' }}>
            <div className="text-dark fw-bold mb-2" style={{fontSize: '0.85rem'}}>Añadir miembros</div>
            <input 
              type="text" 
              className="form-control form-control-sm mb-2" 
              placeholder="Buscar usuario..." 
              value={userSearchQuery}
              onChange={(e) => setUserSearchQuery(e.target.value)}
            />
            <div className="list-group list-group-flush mb-2" style={{maxHeight: '150px', overflowY: 'auto'}}>
              {usersToAdd.filter(u => {
                const query = userSearchQuery.toLowerCase();
                const fullName = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase();
                const username = (u.username || '').toLowerCase();
                return fullName.includes(query) || username.includes(query);
              }).map(u => {
                const isSelected = selectedUsersToAdd.includes(u.id);
                return (
                  <button 
                    key={u.id} 
                    type="button" 
                    className={`list-group-item list-group-item-action py-1 px-2 d-flex align-items-center border-0 ${isSelected ? 'bg-light' : ''}`} 
                    onClick={() => setSelectedUsersToAdd(prev => prev.includes(u.id) ? prev.filter(id => id !== u.id) : [...prev, u.id])}
                  >
                    <img src={u.profile_picture_url} alt="" className="rounded-circle me-2" style={{width: '20px', height: '20px', objectFit: 'cover'}} />
                    <span className="text-truncate text-dark" style={{fontSize: '0.8rem', flex: 1}}>{u.first_name || u.username}</span>
                    {isSelected && <Check size={14} className="text-primary" />}
                  </button>
                );
              })}
              {usersToAdd.length === 0 && <div className="text-muted" style={{fontSize: '0.8rem'}}>No hay usuarios.</div>}
            </div>
            <button 
              className="btn btn-sm text-white w-100" 
              style={{backgroundColor: '#0b5961'}}
              onClick={handleAddUsers} 
              disabled={addingUsers || selectedUsersToAdd.length === 0}
            >
              {addingUsers ? 'Añadiendo...' : 'Añadir al grupo'}
            </button>
          </div>
        )}
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
