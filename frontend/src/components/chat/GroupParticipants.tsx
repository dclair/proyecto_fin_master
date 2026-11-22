import React, { useState, useRef } from 'react';
import useClickOutside from '../../hooks/useClickOutside';
import { ChatUser } from '../../types/chat.types';

export interface GroupParticipantsProps {
  isOpen: boolean;
  onClose: () => void;
  participants?: ChatUser[];
  adminId?: number | null;
}

export const GroupParticipants: React.FC<GroupParticipantsProps> = ({
  isOpen,
  onClose,
  participants = [],
  adminId,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const popoverRef = useRef<HTMLDivElement | null>(null);

  useClickOutside(popoverRef, onClose, isOpen);

  if (!isOpen) return null;

  const filtered = participants.filter((p) => {
    const query = searchQuery.toLowerCase();
    const fullName = `${p.first_name || ''} ${p.last_name || ''}`.toLowerCase();
    const username = (p.username || '').toLowerCase();
    return fullName.includes(query) || username.includes(query);
  });

  return (
    <div
      ref={popoverRef}
      className="position-absolute shadow rounded p-2"
      style={{
        top: '100%',
        right: '10px',
        width: '250px',
        zIndex: 1000,
        border: '1px solid var(--bs-border-color)',
        backgroundColor: 'var(--bs-card-bg)',
        color: 'var(--bs-body-color)',
      }}
    >
      <div className="text-body fw-bold mb-2" style={{ fontSize: '0.85rem' }}>
        Participantes ({participants.length})
      </div>
      <input
        type="text"
        className="form-control form-control-sm mb-2"
        placeholder="Buscar participante..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <div
        className="list-group list-group-flush mb-2"
        style={{ maxHeight: '200px', overflowY: 'auto' }}
      >
        {filtered.map((p) => (
          <div
            key={p.id}
            className="list-group-item py-1 px-2 d-flex align-items-center border-0 bg-transparent text-body"
          >
            <img
              src={p.profile_picture_url || 'https://via.placeholder.com/24'}
              alt=""
              className="rounded-circle me-2"
              style={{ width: '24px', height: '24px', objectFit: 'cover' }}
            />
            <span
              className="text-truncate text-body flex-grow-1"
              style={{ fontSize: '0.8rem' }}
            >
              {p.first_name || p.username}
              {adminId === p.id && (
                <span className="ms-1 badge bg-primary" style={{ fontSize: '0.6rem' }}>
                  Admin
                </span>
              )}
            </span>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="text-muted" style={{ fontSize: '0.8rem' }}>
            No se encontraron participantes.
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupParticipants;
