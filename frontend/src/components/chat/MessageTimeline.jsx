import React from 'react';
import { Trash2, FileText } from 'lucide-react';

const renderMessageWithLinks = (text) => {
  if (!text) return null;
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);

  return parts.map((part, i) => {
    if (part.match(urlRegex)) {
      return (
        <a
          key={i}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className="text-reset text-decoration-underline"
          style={{ fontWeight: '500' }}
        >
          {part}
        </a>
      );
    }
    return part;
  });
};

export const MessageTimeline = ({
  messages,
  loading,
  currentUsername,
  onDeleteMessage,
  messagesEndRef,
}) => {
  if (loading) {
    return (
      <div className="messages-list">
        <div className="loading">Cargando historial...</div>
        <div ref={messagesEndRef} />
      </div>
    );
  }

  return (
    <div className="messages-list">
      {messages.map((msg, idx) => {
        const isMe = msg.sender?.username === currentUsername;

        return (
          <div
            key={msg.id || `temp-${idx}`}
            className={`message-bubble-wrapper ${isMe ? 'me' : 'them'}`}
          >
            <div className="message-bubble position-relative">
              {!isMe && (
                <div className="sender-name">
                  {msg.sender?.first_name || msg.sender?.username}
                </div>
              )}

              {msg.attachment && (
                <div className="message-attachment mb-1">
                  {msg.attachment_type === 'image' && (
                    <a href={msg.attachment} target="_blank" rel="noopener noreferrer">
                      <img
                        src={msg.attachment}
                        alt="Adjunto"
                        style={{
                          maxHeight: '200px',
                          maxWidth: '100%',
                          borderRadius: '8px',
                          cursor: 'pointer',
                        }}
                      />
                    </a>
                  )}
                  {msg.attachment_type === 'video' && (
                    <video
                      controls
                      style={{
                        maxHeight: '200px',
                        maxWidth: '100%',
                        borderRadius: '8px',
                      }}
                    >
                      <source src={msg.attachment} />
                      Tu navegador no soporta el video.
                    </video>
                  )}
                  {msg.attachment_type === 'document' && (
                    <a
                      href={msg.attachment}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="d-flex align-items-center gap-2 p-2 rounded text-decoration-none text-reset"
                      style={{ backgroundColor: 'rgba(0,0,0,0.05)' }}
                    >
                      <FileText size={24} />
                      <span style={{ wordBreak: 'break-all', fontSize: '0.85rem' }}>
                        {msg.attachment.split('/').pop()}
                      </span>
                    </a>
                  )}
                  {msg.attachment_type === 'audio' && (
                    <audio
                      controls
                      src={msg.attachment}
                      className="d-block mt-1"
                      style={{ maxWidth: '100%', height: '40px' }}
                      preload="metadata"
                    />
                  )}
                </div>
              )}

              {msg.content && (
                <div
                  className="message-content"
                  style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                >
                  {renderMessageWithLinks(msg.content)}
                </div>
              )}

              <button
                className={`btn btn-sm btn-link p-0 position-absolute ${
                  isMe ? 'text-danger' : 'text-secondary'
                }`}
                style={{
                  [isMe ? 'left' : 'right']: '-25px',
                  top: '5px',
                  opacity: 0.6,
                }}
                onClick={() => onDeleteMessage(msg.id, isMe)}
                title={isMe ? 'Eliminar mensaje' : 'Eliminar para mí'}
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        );
      })}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageTimeline;

