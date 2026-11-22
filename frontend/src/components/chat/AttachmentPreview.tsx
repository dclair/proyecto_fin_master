import React from 'react';
import { Video, Mic, FileText, FileSpreadsheet, FileArchive, FileCode, X, LucideIcon } from 'lucide-react';

export interface AttachmentPreviewProps {
  selectedFile: File | null;
  previewUrl: string | null;
  onCancel: () => void;
}

interface DocPreviewInfo {
  icon: LucideIcon;
  color: string;
  bgColor: string;
  badge: string;
}

export const AttachmentPreview: React.FC<AttachmentPreviewProps> = ({ selectedFile, previewUrl, onCancel }) => {
  if (!selectedFile) return null;

  const isImage = previewUrl && !['video', 'document', 'audio'].includes(previewUrl);

  const getDocPreview = (): DocPreviewInfo => {
    const ext = (selectedFile.name.includes('.') ? selectedFile.name.split('.').pop() : '')?.toLowerCase() || '';
    if (ext === 'pdf' || selectedFile.type === 'application/pdf') {
      return {
        icon: FileText,
        color: '#dc2626',
        bgColor: '#fee2e2',
        badge: 'PDF',
      };
    }
    if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) {
      return {
        icon: FileSpreadsheet,
        color: '#16a34a',
        bgColor: '#dcfce7',
        badge: ext.toUpperCase(),
      };
    }
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) {
      return {
        icon: FileArchive,
        color: '#d97706',
        bgColor: '#fef3c7',
        badge: ext.toUpperCase(),
      };
    }
    if (['txt', 'md', 'json', 'xml', 'js', 'py', 'html', 'css'].includes(ext)) {
      return {
        icon: FileCode,
        color: '#7c3aed',
        bgColor: '#ede9fe',
        badge: ext.toUpperCase(),
      };
    }
    return {
      icon: FileText,
      color: '#475569',
      bgColor: '#f1f5f9',
      badge: ext ? ext.toUpperCase() : 'DOC',
    };
  };

  const doc = !isImage && previewUrl !== 'video' && previewUrl !== 'audio' ? getDocPreview() : null;

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
      ) : doc ? (
        <div
          className="d-flex align-items-center justify-content-center rounded position-relative flex-shrink-0"
          style={{ height: '60px', width: '60px', backgroundColor: doc.bgColor, color: doc.color }}
        >
          <doc.icon size={26} strokeWidth={2} />
          {doc.badge && (
            <span
              style={{
                position: 'absolute',
                bottom: '4px',
                right: '4px',
                backgroundColor: doc.color,
                color: '#ffffff',
                fontSize: '8px',
                fontWeight: 'bold',
                padding: '1px 3px',
                borderRadius: '3px',
                lineHeight: 1,
              }}
            >
              {doc.badge}
            </span>
          )}
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
        <div className="fw-bold text-dark">{selectedFile.name}</div>
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
