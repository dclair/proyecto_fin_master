import React, { useState, useEffect } from 'react';
import { Users, ArrowLeft } from 'lucide-react';
import chatService from '../api/chat.service';
import { Conversation } from '../types/chat.types';

export interface GroupExplorerProps {
  onBack: () => void;
}

type RequestStatusMap = Record<number, 'sending' | 'sent' | 'error'>;

export const GroupExplorer: React.FC<GroupExplorerProps> = ({ onBack }) => {
  const [groups, setGroups] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [requestStatus, setRequestStatus] = useState<RequestStatusMap>({});

  useEffect(() => {
    chatService
      .getDiscoverableGroups()
      .then((data) => {
        setGroups(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching discoverable groups:', err);
        setLoading(false);
      });
  }, []);

  const handleRequestJoin = async (groupId: number) => {
    setRequestStatus((prev) => ({ ...prev, [groupId]: 'sending' }));

    try {
      await chatService.requestJoinGroup(groupId);
      setRequestStatus((prev) => ({ ...prev, [groupId]: 'sent' }));
    } catch (err) {
      console.error('Error requesting join:', err);
      setRequestStatus((prev) => ({ ...prev, [groupId]: 'error' }));
    }
  };

  return (
    <div className="d-flex flex-column h-100 bg-white">
      <div className="p-3 bg-light border-bottom d-flex align-items-center">
        <button
          type="button"
          className="btn btn-link text-dark p-0 me-3"
          onClick={onBack}
        >
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
          groups.map((g) => (
            <div
              key={g.id}
              className="d-flex align-items-center p-2 mb-2 border rounded shadow-sm"
            >
              <div className="bg-light rounded-circle p-2 me-3 d-flex align-items-center justify-content-center">
                <Users size={20} className="text-secondary" />
              </div>
              <div className="flex-grow-1 text-truncate pe-2">
                <div
                  className="fw-bold text-dark text-truncate"
                  style={{ fontSize: '0.9rem' }}
                >
                  {g.name || `Grupo #${g.id}`}
                </div>
                <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                  {g.participants.length} participantes
                </div>
              </div>
              <button
                type="button"
                className="btn btn-sm btn-primary py-1 px-2"
                style={{ fontSize: '0.8rem' }}
                onClick={() => handleRequestJoin(g.id)}
                disabled={
                  requestStatus[g.id] === 'sending' || requestStatus[g.id] === 'sent'
                }
              >
                {requestStatus[g.id] === 'sent'
                  ? 'Solicitado'
                  : requestStatus[g.id] === 'sending'
                  ? '...'
                  : 'Unirse'}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default GroupExplorer;
