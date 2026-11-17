import React, { useRef } from 'react';
import useClickOutside from '../../hooks/useClickOutside';

export const GroupPendingRequests = ({
  isOpen,
  onClose,
  requests = [],
  onManageRequest,
}) => {
  const popoverRef = useRef(null);

  useClickOutside(popoverRef, onClose, isOpen);

  if (!isOpen) return null;

  return (
    <div
      ref={popoverRef}
      className="position-absolute shadow rounded p-2"
      style={{
        top: '100%',
        right: '10px',
        width: '250px',
        zIndex: 1000,
        border: '1px solid #ccc',
        backgroundColor: 'white',
      }}
    >
      <div className="text-dark fw-bold mb-2" style={{ fontSize: '0.85rem' }}>
        Solicitudes Pendientes
      </div>
      <div
        className="list-group list-group-flush mb-2"
        style={{ maxHeight: '200px', overflowY: 'auto' }}
      >
        {requests.map((r) => (
          <div
            key={r.id}
            className="list-group-item py-2 px-2 d-flex flex-column border-bottom"
          >
            <div className="d-flex align-items-center mb-1">
              <img
                src={r.user.profile_picture_url}
                alt=""
                className="rounded-circle me-2"
                style={{ width: '20px', height: '20px', objectFit: 'cover' }}
              />
              <span
                className="text-truncate text-dark fw-bold"
                style={{ fontSize: '0.8rem' }}
              >
                {r.user.first_name || r.user.username}
              </span>
            </div>
            <div className="d-flex gap-1 mt-1">
              <button
                type="button"
                className="btn btn-sm btn-success py-0 flex-grow-1"
                style={{ fontSize: '0.75rem' }}
                onClick={() => onManageRequest(r.id, 'accept')}
              >
                Aceptar
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline-danger py-0 flex-grow-1"
                style={{ fontSize: '0.75rem' }}
                onClick={() => onManageRequest(r.id, 'reject')}
              >
                Rechazar
              </button>
            </div>
          </div>
        ))}
        {requests.length === 0 && (
          <div className="text-muted" style={{ fontSize: '0.8rem' }}>
            No hay solicitudes pendientes.
          </div>
        )}
      </div>
    </div>
  );
};

export default GroupPendingRequests;

