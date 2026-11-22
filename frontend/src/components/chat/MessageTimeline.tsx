import React from 'react';
import {
  Trash2,
  FileText,
  FileSpreadsheet,
  FileArchive,
  FileCode,
  File as FileIcon,
  Download,
  LucideIcon,
} from 'lucide-react';
import { ChatMessage, AttachmentType } from '../../types/chat.types';

const isImage = (url?: string | null, type?: AttachmentType | null, name?: string | null): boolean => {
  if (type === 'image') return true;
  const target = (name || url || '').toLowerCase();
  return /\.(png|jpe?g|gif|webp|svg)(\?.*)?$/i.test(target);
};

const isVideo = (url?: string | null, type?: AttachmentType | null, name?: string | null): boolean => {
  if (type === 'video') return true;
  const target = (name || url || '').toLowerCase();
  return /\.(mp4|webm|mov)(\?.*)?$/i.test(target);
};

const isAudio = (url?: string | null, type?: AttachmentType | null, name?: string | null): boolean => {
  if (type === 'audio') return true;
  const target = (name || url || '').toLowerCase();
  return /\.(mp3|wav|ogg|m4a)(\?.*)?$/i.test(target);
};

const getAttachmentDisplayName = (msg: ChatMessage): string => {
  if (msg.attachment_name) return msg.attachment_name;
  if (msg.attachment) {
    const clean = msg.attachment.replace(/\/+$/, '');
    const name = clean.split('/').pop();
    if (name && name !== 'attachment') return decodeURIComponent(name);
  }
  return 'Archivo adjunto';
};

interface FileInfo {
  type: string;
  badge: string;
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
  icon: LucideIcon;
  name: string;
}

const getFileInfo = (msg: ChatMessage): FileInfo => {
  const name = getAttachmentDisplayName(msg);
  const ext = (name.includes('.') ? name.split('.').pop() : '')?.toLowerCase() || '';

  if (ext === 'pdf' || (msg.attachment_type === 'document' && ext === 'pdf')) {
    return {
      type: 'pdf',
      badge: 'PDF',
      label: 'Documento PDF',
      color: '#dc2626',
      bgColor: '#fee2e2',
      borderColor: '#fca5a5',
      icon: FileText,
      name,
    };
  }

  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) {
    return {
      type: 'spreadsheet',
      badge: ext.toUpperCase(),
      label: 'Hoja de cálculo',
      color: '#16a34a',
      bgColor: '#dcfce7',
      borderColor: '#86efac',
      icon: FileSpreadsheet,
      name,
    };
  }

  if (['doc', 'docx', 'odt'].includes(ext)) {
    return {
      type: 'word',
      badge: ext.toUpperCase(),
      label: 'Documento de texto',
      color: '#2563eb',
      bgColor: '#dbeafe',
      borderColor: '#93c5fd',
      icon: FileText,
      name,
    };
  }

  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
    return {
      type: 'archive',
      badge: ext.toUpperCase(),
      label: 'Archivo comprimido',
      color: '#d97706',
      bgColor: '#fef3c7',
      borderColor: '#fde68a',
      icon: FileArchive,
      name,
    };
  }

  if (['txt', 'md', 'json', 'xml', 'js', 'py', 'html', 'css'].includes(ext)) {
    return {
      type: 'code',
      badge: ext.toUpperCase() || 'TXT',
      label: 'Archivo de texto/código',
      color: '#7c3aed',
      bgColor: '#ede9fe',
      borderColor: '#ddd6fe',
      icon: FileCode,
      name,
    };
  }

  return {
    type: 'generic',
    badge: ext ? ext.toUpperCase() : 'DOC',
    label: 'Documento adjunto',
    color: '#475569',
    bgColor: '#f1f5f9',
    borderColor: '#cbd5e1',
    icon: FileIcon,
    name,
  };
};

const DocumentAttachment: React.FC<{ msg: ChatMessage }> = ({ msg }) => {
  const fileInfo = getFileInfo(msg);
  const IconComponent = fileInfo.icon;
  if (!msg.attachment) return null;

  const downloadUrl = msg.attachment.includes('?')
    ? `${msg.attachment}&download=1`
    : `${msg.attachment}?download=1`;

  return (
    <div
      className="document-attachment-card d-flex align-items-center justify-content-between gap-3 p-2 rounded-3 my-1"
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid rgba(0,0,0,0.12)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        color: '#1e293b',
        maxWidth: '340px',
        minWidth: '240px',
      }}
    >
      <a
        href={msg.attachment}
        target="_blank"
        rel="noopener noreferrer"
        className="d-flex align-items-center gap-2 text-decoration-none flex-grow-1 overflow-hidden"
        style={{ color: '#1e293b' }}
        title={`Abrir ${fileInfo.name}`}
      >
        <div
          className="d-flex align-items-center justify-content-center rounded-2 flex-shrink-0 position-relative"
          style={{
            width: '42px',
            height: '42px',
            backgroundColor: fileInfo.bgColor,
            border: `1px solid ${fileInfo.borderColor}`,
            color: fileInfo.color,
          }}
        >
          <IconComponent size={22} strokeWidth={2} />
          {fileInfo.badge && (
            <span
              style={{
                position: 'absolute',
                bottom: '-3px',
                right: '-3px',
                backgroundColor: fileInfo.color,
                color: '#ffffff',
                fontSize: '8px',
                fontWeight: 'bold',
                padding: '1px 3px',
                borderRadius: '3px',
                lineHeight: 1,
                letterSpacing: '0.5px',
              }}
            >
              {fileInfo.badge}
            </span>
          )}
        </div>

        <div className="d-flex flex-column overflow-hidden text-start">
          <span
            className="fw-bold text-truncate"
            style={{ fontSize: '0.88rem', lineHeight: '1.25', color: '#0f172a' }}
            title={fileInfo.name}
          >
            {fileInfo.name}
          </span>
          <span
            className="text-muted text-truncate"
            style={{ fontSize: '0.72rem', marginTop: '2px' }}
          >
            {fileInfo.label}
          </span>
        </div>
      </a>

      <a
        href={downloadUrl}
        download={fileInfo.name}
        className="btn btn-sm p-1 rounded-circle flex-shrink-0 d-flex align-items-center justify-content-center"
        style={{
          width: '32px',
          height: '32px',
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          color: fileInfo.color,
        }}
        title={`Descargar ${fileInfo.name}`}
      >
        <Download size={16} strokeWidth={2.2} />
      </a>
    </div>
  );
};

const renderMessageWithLinks = (text: string): React.ReactNode => {
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

export interface MessageTimelineProps {
  messages: ChatMessage[];
  loading: boolean;
  currentUsername: string;
  onDeleteMessage: (messageId: number, isMe: boolean) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

export const MessageTimeline: React.FC<MessageTimelineProps> = ({
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
        const displayName = getAttachmentDisplayName(msg);

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
                  {isImage(msg.attachment, msg.attachment_type, displayName) && (
                    <a href={msg.attachment} target="_blank" rel="noopener noreferrer">
                      <img
                        src={msg.attachment}
                        alt={displayName || 'Adjunto'}
                        style={{
                          maxHeight: '200px',
                          maxWidth: '100%',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          display: 'block',
                          objectFit: 'contain',
                        }}
                      />
                    </a>
                  )}
                  {isVideo(msg.attachment, msg.attachment_type, displayName) && (
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
                  {isAudio(msg.attachment, msg.attachment_type, displayName) && (
                    <audio
                      controls
                      src={msg.attachment}
                      className="d-block mt-1"
                      style={{ maxWidth: '100%', height: '40px' }}
                      preload="metadata"
                    />
                  )}
                  {!isImage(msg.attachment, msg.attachment_type, displayName) &&
                    !isVideo(msg.attachment, msg.attachment_type, displayName) &&
                    !isAudio(msg.attachment, msg.attachment_type, displayName) && (
                      <DocumentAttachment msg={msg} />
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
                type="button"
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
