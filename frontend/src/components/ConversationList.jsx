import React from "react";
import { User, Users } from "lucide-react";

const ConversationList = ({ conversations, onSelect, activeId }) => {
  return (
    <div className="conversation-list">
      {conversations.length === 0 ? (
        <div className="empty-state">No tienes conversaciones aún.</div>
      ) : (
        conversations.map((conv) => {
          const isActive = conv.id === activeId;
          // Mostrar el nombre del otro participante si es 1 a 1, o "Grupo X" si es grupo.
          // Como simplificación, asumimos que el otro participante es el que no soy yo.
          // Pero para que quede bein hecho, mostraremos todos los nombres.
          const title = conv.is_group
            ? "Chat Grupal"
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
                <div className="conv-title">{title}</div>
                {conv.last_message && (
                  <div className="conv-last-msg">
                    {conv.last_message.content}
                  </div>
                )}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default ConversationList;
