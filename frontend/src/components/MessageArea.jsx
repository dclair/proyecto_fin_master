import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, Users, Trash2, UserCheck, UserPlus } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useChatRecorder } from '../hooks/useChatRecorder';
import chatService from '../api/chat.service';

// Subcomponentes presentacionales (Dumb Components)
import MessageTimeline from './chat/MessageTimeline';
import MessageInput from './chat/MessageInput';
import AttachmentPreview from './chat/AttachmentPreview';
import GroupParticipants from './chat/GroupParticipants';
import GroupPendingRequests from './chat/GroupPendingRequests';
import GroupAddMember from './chat/GroupAddMember';

/**
 * MessageArea (Smart Container Component)
 * Pattern: Container - Presentational (Gentleman Programming)
 * Responsibilities: State orchestration, API service calls, and component composition.
 */
const MessageArea = ({
  conversationId,
  conversationTitle,
  isGroup,
  activeConversation,
  onBack,
  onConversationDeleted,
  currentUsername,
}) => {
  // WebSocket hook
  const { messages, setMessages, sendMessage, setInitialMessages } = useWebSocket(conversationId);

  // UI state
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Group Admin UI states
  const [showParticipants, setShowParticipants] = useState(false);
  const [showPending, setShowPending] = useState(false);
  const [showAddMember, setShowAddMember] = useState(false);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [usersToAdd, setUsersToAdd] = useState([]);
  const [addingUsers, setAddingUsers] = useState(false);

  const messagesEndRef = useRef(null);

  // Auth & Permissions
  const me = activeConversation?.participants?.find((p) => p.username === currentUsername);
  const isAdmin = isGroup && me && activeConversation?.admin === me.id;

  // Voice recording integration
  const handleAudioRecorded = useCallback((audioFile) => {
    setSelectedFile(audioFile);
    setPreviewUrl('audio');
  }, []);

  const {
    isRecording,
    formattedTime,
    startRecording,
    stopRecording,
    cancelRecording,
  } = useChatRecorder({
    onRecorded: handleAudioRecorded,
  });

  // Marcar como leído
  const markAsRead = useCallback(() => {
    if (!conversationId) return;
    chatService.markAsRead(conversationId).catch((err) =>
      console.warn('[MessageArea]: Error al marcar como leído:', err)
    );
  }, [conversationId]);

  // Cargar historial de mensajes
  useEffect(() => {
    setLoading(true);
    chatService
      .getMessages(conversationId)
      .then((data) => {
        setInitialMessages(data);
        setLoading(false);
        markAsRead();
      })
      .catch((err) => {
        console.error('[MessageArea]: Error cargando mensajes:', err);
        setLoading(false);
      });
  }, [conversationId, setInitialMessages, markAsRead]);

  // Scroll automático y auto-lectura al llegar mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (messages.length > 0) {
      markAsRead();
    }
  }, [messages, markAsRead]);

  // Cargar solicitudes pendientes para el administrador
  useEffect(() => {
    if (isAdmin) {
      chatService
        .getPendingRequests()
        .then((requests) => {
          setPendingRequests(requests.filter((r) => r.conversation === conversationId));
        })
        .catch(console.error);
    }
  }, [isAdmin, conversationId, showPending]);

  // Cargar lista de usuarios al abrir el modal de añadir participantes
  useEffect(() => {
    if (showAddMember) {
      chatService
        .getUsers()
        .then((users) => setUsersToAdd(users))
        .catch((err) => console.error('[MessageArea]: Error cargando usuarios:', err));
    }
  }, [showAddMember]);

  // Cancelar archivo seleccionado
  const handleCancelAttachment = () => {
    setSelectedFile(null);
    if (previewUrl && !['video', 'document', 'audio'].includes(previewUrl)) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
  };

  // Manejar selección de archivos desde el input
  const handleFileSelect = (file) => {
    setSelectedFile(file);
    const mime = file.type;
    if (mime.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(file));
    } else if (mime.startsWith('video/')) {
      setPreviewUrl('video');
    } else {
      setPreviewUrl('document');
    }
  };

  // Enviar mensaje o adjunto
  const handleSend = async (e) => {
    e.preventDefault();
    if (uploading) return;

    if (selectedFile) {
      setUploading(true);
      try {
        await chatService.uploadAttachment(conversationId, selectedFile, inputValue);
        setInputValue('');
        handleCancelAttachment();
      } catch (err) {
        console.error('[MessageArea]: Error subiendo archivo:', err);
        alert('Ocurrió un error al subir el archivo.');
      } finally {
        setUploading(false);
      }
    } else if (inputValue.trim()) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  // Eliminar o esconder mensaje
  const handleDeleteMessage = async (messageId, isMe) => {
    let type = 'me';
    if (isMe) {
      const delAll = window.confirm('¿Deseas eliminar este mensaje para TODOS?');
      if (delAll) {
        type = 'all';
      } else {
        const delMe = window.confirm('¿Deseas eliminar este mensaje solo para TI?');
        if (!delMe) return;
      }
    } else {
      const delMe = window.confirm('¿Deseas eliminar este mensaje solo para TI?');
      if (!delMe) return;
    }

    try {
      if (type === 'all') {
        await chatService.deleteMessage(messageId);
      } else {
        await chatService.hideMessage(messageId);
        setMessages((prev) => prev.filter((m) => m.id !== messageId));
      }
    } catch (err) {
      console.error('[MessageArea]: Error al procesar mensaje:', err);
      alert('Hubo un error al intentar eliminar u ocultar el mensaje.');
    }
  };

  // Eliminar conversación completa
  const handleDeleteConversation = async () => {
    const confirmed = window.confirm(
      '¿Estás seguro de que quieres eliminar este chat permanentemente? Esta acción no se puede deshacer y borrará el chat para todos.'
    );
    if (!confirmed) return;

    try {
      await chatService.deleteConversation(conversationId);
      if (onConversationDeleted) onConversationDeleted();
      else onBack();
    } catch (err) {
      console.error('[MessageArea]: Error al eliminar conversación:', err);
      alert('No tienes permiso para eliminar este chat o hubo un error.');
    }
  };

  // Gestionar solicitudes de acceso a grupo
  const handleManageRequest = async (requestId, action) => {
    try {
      await chatService.manageJoinRequest(requestId, action);
      setPendingRequests((prev) => prev.filter((r) => r.id !== requestId));
    } catch (err) {
      console.error('[MessageArea]: Error gestionando solicitud:', err);
    }
  };

  // Añadir miembros seleccionados al grupo
  const handleAddUsers = async (userIds) => {
    setAddingUsers(true);
    try {
      await chatService.addUsersToGroup(conversationId, userIds);
      setShowAddMember(false);
    } catch (err) {
      console.error('[MessageArea]: Error añadiendo miembros:', err);
      alert('No se pudieron añadir los usuarios al grupo.');
    } finally {
      setAddingUsers(false);
    }
  };

  return (
    <div className="message-area">
      {/* Header Container */}
      <div className="message-header" style={{ position: 'relative' }}>
        <button type="button" className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <div className="header-title text-truncate" style={{ maxWidth: '220px' }}>
          {conversationTitle || `Chat #${conversationId}`}
        </div>

        <div className="d-flex ms-auto gap-2">
          {isGroup && (
            <button
              type="button"
              className="btn btn-sm btn-link text-primary p-0 d-flex align-items-center"
              onClick={() => setShowParticipants((prev) => !prev)}
              title="Ver participantes"
              style={{ textDecoration: 'none' }}
            >
              <Users size={18} />
              <span className="ms-1" style={{ fontSize: '0.75rem', fontWeight: 'bold' }}>
                {activeConversation?.participants?.length || 0}
              </span>
            </button>
          )}

          {(!isGroup || isAdmin) && (
            <button
              type="button"
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
                  type="button"
                  className="btn btn-sm btn-link text-warning p-0 position-relative"
                  onClick={() => setShowPending((prev) => !prev)}
                  title="Solicitudes de acceso"
                >
                  <UserCheck size={18} />
                  <span
                    className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                    style={{ fontSize: '0.5rem', padding: '0.15rem 0.25rem' }}
                  >
                    {pendingRequests.length}
                  </span>
                </button>
              )}
              <button
                type="button"
                className="btn btn-sm btn-link text-dark p-0"
                onClick={() => setShowAddMember((prev) => !prev)}
                title="Añadir participante"
              >
                <UserPlus size={18} />
              </button>
            </>
          )}
        </div>

        {/* Popovers presentacionales */}
        <GroupPendingRequests
          isOpen={showPending}
          onClose={() => setShowPending(false)}
          requests={pendingRequests}
          onManageRequest={handleManageRequest}
        />

        <GroupParticipants
          isOpen={showParticipants && isGroup}
          onClose={() => setShowParticipants(false)}
          participants={activeConversation?.participants}
          adminId={activeConversation?.admin}
        />

        <GroupAddMember
          isOpen={showAddMember}
          onClose={() => setShowAddMember(false)}
          users={usersToAdd}
          onAddUsers={handleAddUsers}
          adding={addingUsers}
        />
      </div>

      {/* Timeline presentacional */}
      <MessageTimeline
        messages={messages}
        loading={loading}
        currentUsername={currentUsername}
        onDeleteMessage={handleDeleteMessage}
        messagesEndRef={messagesEndRef}
      />

      {/* Previsualización de adjuntos */}
      <AttachmentPreview
        selectedFile={selectedFile}
        previewUrl={previewUrl}
        onCancel={handleCancelAttachment}
      />

      {/* Input de mensajes y media recorder */}
      <MessageInput
        inputValue={inputValue}
        onChangeInput={setInputValue}
        onSubmit={handleSend}
        onFileSelect={handleFileSelect}
        isRecording={isRecording}
        recordingTimeFormatted={formattedTime}
        onStartRecording={startRecording}
        onStopRecording={stopRecording}
        onCancelRecording={cancelRecording}
        uploading={uploading}
        hasAttachment={Boolean(selectedFile)}
      />
    </div>
  );
};

export default MessageArea;
