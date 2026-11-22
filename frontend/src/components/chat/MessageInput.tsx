import React, { useState, useRef, ChangeEvent, FormEvent } from 'react';
import { Send, Smile, Paperclip, Mic, Trash } from 'lucide-react';
import EmojiPicker, { EmojiClickData, Theme } from 'emoji-picker-react';
import useClickOutside from '../../hooks/useClickOutside';
import { useHostTheme } from '../../hooks/useHostTheme';

export interface MessageInputProps {
  inputValue: string;
  onChangeInput: (value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onFileSelect: (file: File) => void;
  isRecording: boolean;
  recordingTimeFormatted: string;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onCancelRecording: () => void;
  uploading: boolean;
  hasAttachment: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  inputValue,
  onChangeInput,
  onSubmit,
  onFileSelect,
  isRecording,
  recordingTimeFormatted,
  onStartRecording,
  onStopRecording,
  onCancelRecording,
  uploading,
  hasAttachment,
}) => {
  const hostTheme = useHostTheme();
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const emojiPickerRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Cerrar emoji picker al hacer clic afuera
  useClickOutside(emojiPickerRef, () => setShowEmojiPicker(false), showEmojiPicker);

  const handleEmojiClick = (emojiObject: EmojiClickData) => {
    onChangeInput(inputValue + emojiObject.emoji);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const mimeType = file.type;
    const MB = 1024 * 1024;

    if (mimeType.startsWith('video/') && file.size > 15 * MB) {
      alert('El vídeo es demasiado grande (Máximo 15 MB).');
      e.target.value = '';
      return;
    }

    if (!mimeType.startsWith('video/') && file.size > 5 * MB) {
      alert('El archivo es demasiado grande (Máximo 5 MB).');
      e.target.value = '';
      return;
    }

    onFileSelect(file);
    e.target.value = '';
  };

  return (
    <form className="message-input-area" onSubmit={onSubmit} style={{ position: 'relative' }}>
      {showEmojiPicker && (
        <div
          ref={emojiPickerRef}
          style={{
            position: 'absolute',
            bottom: '60px',
            left: '10px',
            zIndex: 1000,
            boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
            borderRadius: '8px',
          }}
        >
          <EmojiPicker
            onEmojiClick={handleEmojiClick}
            width={300}
            height={350}
            theme={hostTheme === 'dark' ? Theme.DARK : Theme.LIGHT}
            searchPlaceholder="Buscar emoji..."
            lazyLoadEmojis={true}
          />
        </div>
      )}

      {isRecording ? (
        <div className="d-flex align-items-center justify-content-between w-100 px-2 py-1">
          <div className="d-flex align-items-center text-danger">
            <div
              className="recording-dot me-2"
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: 'red',
                animation: 'pulse 1s infinite',
              }}
            />
            <span className="fw-bold">{recordingTimeFormatted}</span>
          </div>
          <div className="d-flex align-items-center gap-3">
            <button
              type="button"
              onClick={onCancelRecording}
              className="btn btn-link text-secondary p-0"
              title="Cancelar grabación"
            >
              <Trash size={20} />
            </button>
            <button
              type="button"
              onClick={onStopRecording}
              className="btn btn-danger rounded-circle p-0 d-flex align-items-center justify-content-center text-white"
              title="Enviar audio"
              style={{ width: '32px', height: '32px' }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      ) : (
        <>
          <button
            type="button"
            onClick={() => setShowEmojiPicker((val) => !val)}
            style={{
              background: 'none',
              border: 'none',
              color: showEmojiPicker ? 'var(--hubs-primary, #0b5961)' : 'var(--bs-secondary-color)',
              cursor: 'pointer',
              padding: '0 8px 0 0',
              display: 'flex',
              alignItems: 'center',
            }}
            title="Insertar emoji"
          >
            <Smile size={24} />
          </button>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--bs-secondary-color)',
              cursor: 'pointer',
              padding: '0 8px 0 0',
              display: 'flex',
              alignItems: 'center',
            }}
            title="Adjuntar archivo"
          >
            <Paperclip size={24} />
          </button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />

          <input
            type="text"
            value={inputValue}
            onChange={(e) => onChangeInput(e.target.value)}
            placeholder="Escribe un mensaje..."
            className="msg-input"
          />

          {inputValue.trim() || hasAttachment ? (
            <button type="submit" className="send-btn" disabled={uploading}>
              <Send size={18} />
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-link text-secondary p-0 ms-1"
              onClick={onStartRecording}
              title="Grabar nota de voz"
              style={{ border: 'none', background: 'none' }}
            >
              <Mic size={22} />
            </button>
          )}
        </>
      )}
    </form>
  );
};

export default MessageInput;
