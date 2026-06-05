import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, ArrowLeft, Send } from 'lucide-react';

const GroupExplorer = ({ onBack }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [requestStatus, setRequestStatus] = useState({}); // { id: 'sending' | 'sent' | 'error' }

  useEffect(() => {
    axios.get('/api/chat/groups/discover/')
      .then(res => {
        setGroups(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching discoverable groups:", err);
        setLoading(false);
      });
  }, []);

  const handleRequestJoin = (groupId) => {
    setRequestStatus(prev => ({ ...prev, [groupId]: 'sending' }));
    
    const token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    axios.post(`/api/chat/groups/${groupId}/request_join/`, {}, {
      headers: { 'X-CSRFToken': token }
    })
    .then(() => {
      setRequestStatus(prev => ({ ...prev, [groupId]: 'sent' }));
    })
    .catch(err => {
      console.error("Error requesting join:", err);
      setRequestStatus(prev => ({ ...prev, [groupId]: 'error' }));
    });
  };

  return (
    <div className="d-flex flex-column h-100 bg-white">
      <div className="p-3 bg-light border-bottom d-flex align-items-center">
        <button className="btn btn-link text-dark p-0 me-3" onClick={onBack}>
          <ArrowLeft size={20} />
        </button>
        <h6 className="m-0 fw-bold">Explorar Grupos</h6>
      </div>

      <div className="flex-grow-1 overflow-auto p-2">
        {loading ? (
          <div className="text-center p-4 text-muted">Cargando grupos...</div>
        ) : groups.length === 0 ? (
          <div className="text-center p-4 text-muted">No hay nuevos grupos públicos disponibles.</div>
        ) : (
          groups.map(g => (
            <div key={g.id} className="d-flex align-items-center p-2 mb-2 border rounded shadow-sm">
              <div className="bg-light rounded-circle p-2 me-3 d-flex align-items-center justify-content-center">
                <Users size={20} className="text-secondary" />
              </div>
              <div className="flex-grow-1 text-truncate pe-2">
                <div className="fw-bold text-dark text-truncate" style={{fontSize: '0.9rem'}}>{g.name || `Grupo #${g.id}`}</div>
                <div className="text-muted" style={{fontSize: '0.75rem'}}>{g.participants.length} participantes</div>
              </div>
              <button 
                className="btn btn-sm btn-primary py-1 px-2"
                style={{fontSize: '0.8rem'}}
                onClick={() => handleRequestJoin(g.id)}
                disabled={requestStatus[g.id] === 'sending' || requestStatus[g.id] === 'sent'}
              >
                {requestStatus[g.id] === 'sent' ? 'Solicitado' : requestStatus[g.id] === 'sending' ? '...' : 'Unirse'}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default GroupExplorer;
