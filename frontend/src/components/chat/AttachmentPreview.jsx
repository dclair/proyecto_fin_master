import React from 'react';
import { Video, Mic, FileText, X } from 'lucide-react';

export const AttachmentPreview = ({ selectedFile, previewUrl, onCancel }) => {
  if (!selectedFile) return null;

  const isImage = previewUrl && !['video', 'document', 'audio'].includes(previewUrl);

  return (
    <div
      className="p-2 border-top bg-light position-relative"
      style={{ display: 'flex', alignItems: 'center', gap: '10px' }}
    >
      {isImage ? (
        <img
          src={previewUrl}
          alt="Preview"
          style={{ height: '60px', borderRadius: '4px', objectFit: 'cover' }}
        />
      ) : previewUrl === 'video' ? (
        <div
          className="d-flex align-items-center justify-content-center bg-secondary text-white rounded"
          style={{ height: '60px', width: '60px' }}
        >
          <Video size={24} />
        </div>
      ) : previewUrl === 'audio' ? (
        <div
          className="d-flex align-items-center justify-content-center bg-secondary text-white rounded"
          style={{ height: '60px', width: '60px' }}
        >
          <Mic size={24} />
        </div>
      ) : (
        <div
          className="d-flex align-items-center justify-content-center bg-secondary text-white rounded"
          style={{ height: '60px', width: '60px' }}
        >
          <FileText size={24} />
        </div>
      )}

      <div className="text-truncate flex-grow-1" style={{ fontSize: '0.8rem' }}>
        <div className="fw-bold">{selectedFile.name}</div>
        <div className="text-muted">
          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
        </div>
      </div>

      <button
        type="button"
        className="btn btn-sm btn-light rounded-circle p-1"
        onClick={onCancel}
        style={{ border: '1px solid #ccc', flexShrink: 0 }}
        title="Cancelar adjunto"
      >
        <X size={14} className="text-danger" />
      </button>
    </div>
  );
};

export default AttachmentPreview;

