import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowLeft, MessageSquarePlus } from 'lucide-react';

const UserExplorer = ({ onBack, onStartChat }) => {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch users (already exists at /api/chat/users/)
    axios.get('/api/chat/users/')
      .then(response => {
        setUsers(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error cargando usuarios:", error);
        setLoading(false);
      });
  }, []);

  const filteredUsers = users.filter(user => {
    const query = searchQuery.toLowerCase();
    const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase();
    const username = (user.username || '').toLowerCase();
    return fullName.includes(query) || username.includes(query);
  });

  return (
    <div className="d-flex flex-column h-100 bg-white">
      <div className="p-3 border-bottom d-flex align-items-center bg-light">
        <button className="btn btn-sm btn-link text-dark p-0 me-3" onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <h5 className="mb-0 fw-bold">Buscar Usuario</h5>
      </div>

      <div className="p-3 border-bottom">
        <input 
          type="text" 
          className="form-control" 
          placeholder="Buscar por nombre o usuario..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="flex-grow-1 overflow-auto p-2">
        {loading ? (
          <div className="text-center p-4 text-muted">Cargando usuarios...</div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center p-4 text-muted">No se encontraron usuarios.</div>
        ) : (
          <div className="list-group list-group-flush">
            {filteredUsers.map(user => (
              <div key={user.id} className="list-group-item list-group-item-action d-flex align-items-center border-0 rounded mb-1" style={{cursor: 'pointer'}} onClick={() => onStartChat(user.id)}>
                <img 
                  src={user.profile_picture_url || 'https://via.placeholder.com/40'} 
                  alt="" 
                  className="rounded-circle me-3" 
                  style={{width: '40px', height: '40px', objectFit: 'cover'}} 
                />
                <div className="flex-grow-1">
                  <div className="fw-bold text-dark">{user.first_name || user.username} {user.last_name}</div>
                  <div className="text-muted" style={{fontSize: '0.8rem'}}>@{user.username}</div>
                </div>
                <button className="btn btn-sm btn-outline-primary rounded-circle p-2">
                  <MessageSquarePlus size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserExplorer;
