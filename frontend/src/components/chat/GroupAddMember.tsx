import React, { useState, useRef } from 'react';
import { Check } from 'lucide-react';
import useClickOutside from '../../hooks/useClickOutside';
import { ChatUser } from '../../types/chat.types';

export interface GroupAddMemberProps {
  isOpen: boolean;
  onClose: () => void;
  users?: ChatUser[];
  onAddUsers: (userIds: number[]) => Promise<void>;
  adding?: boolean;
}

export const GroupAddMember: React.FC<GroupAddMemberProps> = ({
  isOpen,
  onClose,
  users = [],
  onAddUsers,
  adding = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const popoverRef = useRef<HTMLDivElement | null>(null);

  useClickOutside(popoverRef, () => {
    onClose();
    setSearchQuery('');
    setSelectedUserIds([]);
  }, isOpen);

  if (!isOpen) return null;

  const toggleSelect = (userId: number) => {
    setSelectedUserIds((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  const handleConfirm = () => {
    if (selectedUserIds.length === 0) return;
    onAddUsers(selectedUserIds).then(() => {
      setSelectedUserIds([]);
      setSearchQuery('');
    });
  };

  const filtered = users.filter((u) => {
    const q = searchQuery.toLowerCase();
    const fullName = `${u.first_name || ''} ${u.last_name || ''}`.toLowerCase();
    const username = (u.username || '').toLowerCase();
    const email = (u.email || '').toLowerCase();
    return fullName.includes(q) || username.includes(q) || email.includes(q);
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
        Añadir miembros
      </div>
      <input
        type="text"
        className="form-control form-control-sm mb-2"
        placeholder="Buscar usuario..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <div
        className="list-group list-group-flush mb-2"
        style={{ maxHeight: '150px', overflowY: 'auto' }}
      >
        {filtered.map((u) => {
          const isSelected = selectedUserIds.includes(u.id);
          return (
            <button
              key={u.id}
              type="button"
              className={`list-group-item list-group-item-action py-1 px-2 d-flex align-items-center border-0 ${
                isSelected ? 'bg-primary-subtle' : 'bg-transparent text-body'
              }`}
              onClick={() => toggleSelect(u.id)}
            >
              <img
                src={u.profile_picture_url || 'https://via.placeholder.com/28'}
                alt=""
                className="rounded-circle me-2"
                style={{ width: '28px', height: '28px', objectFit: 'cover' }}
              />
              <div
                className="text-truncate text-body"
                style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
              >
                <span style={{ fontSize: '0.8rem' }}>
                  {u.first_name || u.username}
                </span>
                <span className="text-muted" style={{ fontSize: '0.65rem' }}>
                  {u.email}
                </span>
              </div>
              {isSelected && <Check size={14} className="text-primary" />}
            </button>
          );
        })}
        {filtered.length === 0 && (
          <div className="text-muted" style={{ fontSize: '0.8rem' }}>
            No hay usuarios.
          </div>
        )}
      </div>
      <button
        type="button"
        className="btn btn-sm text-white w-100"
        style={{ backgroundColor: 'var(--hubs-primary, #0b5961)' }}
        onClick={handleConfirm}
        disabled={adding || selectedUserIds.length === 0}
      >
        {adding ? 'Añadiendo...' : 'Añadir al grupo'}
      </button>
    </div>
  );
};

export default GroupAddMember;
