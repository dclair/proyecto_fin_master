import React, { useState, useEffect } from 'react';
import { ArrowLeft, Users, Check } from 'lucide-react';
import chatService from '../api/chat.service';

const GroupCreator = ({ onBack, onGroupCreated }) => {
  const [users, setUsers] = useState([]);
  const [selectedUserIds, setSelectedUserIds] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    chatService
      .getUsers()
      .then((data) => setUsers(data))
      .catch((err) => {
        console.error('Error al cargar usuarios:', err);
        setError('Error al cargar la lista de usuarios.');
      });
  }, []);

  const filteredUsers = users.filter((user) => {
    const query = searchQuery.toLowerCase();
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase();
    const username = (user.username || '').toLowerCase();
    const email = (user.email || '').toLowerCase();
    return fullName.includes(query) || username.includes(query) || email.includes(query);
  });

  const toggleUser = (userId) => {
    setSelectedUserIds((prev) => {
      if (prev.includes(userId)) {
        return prev.filter((id) => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };

  const handleCreateGroup = async () => {
    if (!groupName.trim()) {
      setError('El nombre del grupo es obligatorio.');
      return;
    }
    if (selectedUserIds.length < 1) {
      setError('Debes seleccionar al menos un participante.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const newGroup = await chatService.createGroup(groupName, selectedUserIds);
      onGroupCreated(newGroup.id);
    } catch (err) {
      console.error('Error al crear el grupo:', err);
      setError(err?.response?.data?.error || 'Error al crear el grupo.');
      setLoading(false);
    }
  };

  return (
    <div className="group-creator d-flex flex-column h-100 bg-white">
      <div className="p-3 border-bottom d-flex align-items-center">
        <button
          type="button"
          onClick={onBack}
          className="btn btn-sm btn-link text-secondary p-0 me-3"
          title="Volver"
        >
          <ArrowLeft size={20} />
        </button>
        <h6 className="mb-0 fw-bold d-flex align-items-center gap-2">
          <Users size={18} />
          Nuevo Grupo
        </h6>
      </div>

      <div className="p-3 flex-grow-1 overflow-auto">
        {error && (
          <div className="alert alert-danger p-2 text-center" style={{ fontSize: '0.85rem' }}>
            {error}
          </div>
        )}

        <div className="mb-3">
          <label className="form-label fw-bold text-muted" style={{ fontSize: '0.85rem' }}>
            Nombre del Grupo
          </label>
          <input
            type="text"
            className="form-control form-control-sm"
            placeholder="Ej: Terapeutas de Madrid"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
          />
        </div>

        <div className="mb-2">
          <label className="form-label fw-bold text-muted" style={{ fontSize: '0.85rem' }}>
            Añadir Participantes ({selectedUserIds.length} seleccionados)
          </label>
          <input
            type="text"
            className="form-control form-control-sm mb-2"
            placeholder="Buscar por nombre, usuario o email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="list-group list-group-flush mb-3">
          {filteredUsers.map((user) => {
            const isSelected = selectedUserIds.includes(user.id);
            return (
              <button
                key={user.id}
                type="button"
                className={`list-group-item list-group-item-action d-flex align-items-center p-2 rounded mb-1 border-0 ${
                  isSelected ? 'bg-light' : ''
                }`}
                onClick={() => toggleUser(user.id)}
              >
                <img
                  src={user.profile_picture_url || 'https://via.placeholder.com/32'}
                  alt=""
                  className="rounded-circle me-2"
                  style={{ width: '32px', height: '32px', objectFit: 'cover' }}
                />
                <div className="flex-grow-1 text-truncate text-start pe-2">
                  <div className="fw-bold text-dark text-truncate" style={{ fontSize: '0.85rem' }}>
                    {user.first_name || user.username} {user.last_name}
                  </div>
                  <div className="text-muted text-truncate" style={{ fontSize: '0.75rem' }}>
                    @{user.username} {user.email && `• ${user.email}`}
                  </div>
                </div>
                {isSelected && <Check size={16} className="text-primary" />}
              </button>
            );
          })}
        </div>
      </div>

      <div className="p-3 border-top bg-light">
        <button
          type="button"
          className="btn btn-sm text-white w-100 fw-bold py-2"
          style={{ backgroundColor: '#0b5961' }}
          onClick={handleCreateGroup}
          disabled={loading}
        >
          {loading ? 'Creando grupo...' : 'Crear Grupo'}
        </button>
      </div>
    </div>
  );
};

export default GroupCreator;
