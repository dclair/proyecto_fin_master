import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, Users, Check } from 'lucide-react';

const GroupCreator = ({ onBack, onGroupCreated }) => {
  const [users, setUsers] = useState([]);
  const [selectedUserIds, setSelectedUserIds] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Cargar la lista de usuarios elegibles para el grupo
    axios.get('/api/chat/users/')
      .then(res => setUsers(res.data))
      .catch(err => {
        console.error("Error al cargar usuarios:", err);
        setError("Error al cargar la lista de usuarios.");
      });
  }, []);

  const filteredUsers = users.filter(user => {
    const query = searchQuery.toLowerCase();
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase();
    const username = (user.username || '').toLowerCase();
    const email = (user.email || '').toLowerCase();
    return fullName.includes(query) || username.includes(query) || email.includes(query);
  });

  const toggleUser = (userId) => {
    setSelectedUserIds(prev => {
      if (prev.includes(userId)) {
        return prev.filter(id => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };

  const handleCreateGroup = () => {
    if (!groupName.trim()) {
      setError("El nombre del grupo es obligatorio.");
      return;
    }
    if (selectedUserIds.length < 1) {
      setError("Debes seleccionar al menos un participante.");
      return;
    }

    setLoading(true);
    setError('');

    const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    
    axios.post('/api/chat/groups/create/', {
      name: groupName.trim(),
      user_ids: selectedUserIds
    }, {
      headers: {
        'X-CSRFToken': token
      }
    })
    .then(response => {
      onGroupCreated(response.data.id);
    })
    .catch(err => {
      console.error("Error al crear el grupo:", err);
      setError(err.response?.data?.error || "Error al crear el grupo.");
      setLoading(false);
    });
  };

  return (
    <div className="group-creator d-flex flex-column h-100 bg-white">
      <div className="p-3 border-bottom d-flex align-items-center">
        <button 
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
        {error && <div className="alert alert-danger p-2 text-center" style={{fontSize: '0.85rem'}}>{error}</div>}

        <div className="mb-3">
          <label className="form-label fw-bold text-muted" style={{fontSize: '0.85rem'}}>Nombre del Grupo</label>
          <input 
            type="text" 
            className="form-control form-control-sm" 
            placeholder="Ej: Terapeutas de Madrid"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            maxLength={50}
          />
        </div>

        <div className="mb-2">
          <label className="form-label fw-bold text-muted" style={{fontSize: '0.85rem'}}>
            Participantes ({selectedUserIds.length} seleccionados)
          </label>
          <div className="mb-2">
            <input 
              type="text" 
              className="form-control form-control-sm" 
              placeholder="Buscar por nombre, usuario o email..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="list-group list-group-flush border rounded" style={{maxHeight: '200px', overflowY: 'auto'}}>
            {filteredUsers.length === 0 ? (
              <div className="p-3 text-center text-muted" style={{fontSize: '0.85rem'}}>No se encontraron usuarios.</div>
            ) : (
              filteredUsers.map(user => {
                const isSelected = selectedUserIds.includes(user.id);
                return (
                  <button
                    key={user.id}
                    type="button"
                    className={`list-group-item list-group-item-action d-flex align-items-center p-2 border-0 border-bottom ${isSelected ? 'bg-light' : ''}`}
                    onClick={() => toggleUser(user.id)}
                  >
                    <div className="position-relative me-3">
                      <img 
                        src={user.profile_picture_url} 
                        alt={user.username}
                        className="rounded-circle"
                        style={{width: '32px', height: '32px', objectFit: 'cover'}}
                      />
                      {isSelected && (
                        <div className="position-absolute bottom-0 end-0 bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style={{width: '14px', height: '14px', right: '-2px', bottom: '-2px'}}>
                          <Check size={10} strokeWidth={4} />
                        </div>
                      )}
                    </div>
                    <div className="text-truncate" style={{fontSize: '0.9rem'}}>
                      <strong>{user.first_name || user.username}</strong>
                      {user.email && <div className="text-muted text-truncate" style={{fontSize: '0.75rem'}}>{user.email}</div>}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>

      <div className="p-3 border-top bg-light text-end">
        <button 
          className="btn btn-sm text-white px-4 fw-bold w-100" 
          style={{backgroundColor: '#0b5961'}}
          onClick={handleCreateGroup}
          disabled={loading || !groupName.trim() || selectedUserIds.length === 0}
        >
          {loading ? 'Creando...' : 'Crear Grupo'}
        </button>
      </div>
    </div>
  );
};

export default GroupCreator;
