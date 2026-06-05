import React from "react";
import { User, Users, Plus } from "lucide-react";

const ConversationList = ({ conversations, onSelect, activeId, onCreateGroup, onExploreGroups }) => {
  return (
    <div className="conversation-list d-flex flex-column h-100">
      <div className="p-2 border-bottom text-center d-flex gap-2">
        <button 
          className="btn btn-sm btn-outline-secondary flex-grow-1 d-flex align-items-center justify-content-center gap-1 fw-bold"
          onClick={onCreateGroup}
        >
          <Plus size={16} /> Nuevo Grupo
        </button>
        <button 
          className="btn btn-sm btn-outline-primary flex-grow-1 d-flex align-items-center justify-content-center gap-1 fw-bold"
          onClick={onExploreGroups}
          title="Explorar Grupos"
        >
          <Users size={16} /> Explorar
        </button>
      </div>
      
      <div className="flex-grow-1 overflow-auto">
        {conversations.length === 0 ? (
          <div className="empty-state p-4 text-center text-muted">No tienes conversaciones aún.</div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeId;
            const title = conv.is_group
              ? (conv.name || "Chat Grupal")
              : conv.participants
                  .map((p) => p.first_name || p.username)
                  .join(", ");

            return (
              <div
                key={conv.id}
                className={`conversation-item ${isActive ? "active" : ""}`}
                onClick={() => onSelect(conv.id)}
              >
                <div className="avatar">
                  {conv.is_group ? <Users size={20} /> : <User size={20} />}
                </div>
                <div className="conv-details">
                  <div className="conv-title d-flex justify-content-between align-items-center">
                    <span className="text-truncate">{title}</span>
                    {conv.unread_count > 0 && (
                      <span className="badge bg-danger rounded-pill ms-2" style={{fontSize: '0.65rem'}}>
                        {conv.unread_count}
                      </span>
                    )}
                  </div>
                  {conv.last_message && (
                    <div className={`conv-last-msg ${conv.unread_count > 0 ? 'fw-bold text-dark' : ''}`}>
                      {conv.last_message.content}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ConversationList;
