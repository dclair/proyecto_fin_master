/**
 * Chat API Service Layer
 * Decouples React UI from backend REST endpoints.
 */
import httpClient from './httpClient';
import { 
  Conversation, 
  ChatMessage, 
  ChatUser, 
  JoinRequest 
} from '../types/chat.types';

export const chatService = {
  /**
   * Obtiene la lista de conversaciones activas
   */
  async getConversations(): Promise<Conversation[]> {
    const response = await httpClient.get<Conversation[]>('conversations/');
    return response.data;
  },

  /**
   * Consulta el número total de mensajes no leídos
   */
  async getUnreadCount(): Promise<number> {
    const response = await httpClient.get<{ unread_count: number }>('unread_count/');
    return response.data.unread_count || 0;
  },

  /**
   * Inicia o recupera una conversación privada con un usuario
   */
  async createPrivateConversation(userId: number): Promise<Conversation> {
    const response = await httpClient.post<Conversation>('conversations/create/', { user_id: userId });
    return response.data;
  },

  /**
   * Crea un nuevo grupo de chat
   */
  async createGroup(name: string, userIds: number[]): Promise<Conversation> {
    const response = await httpClient.post<Conversation>('groups/create/', {
      name: name.trim(),
      user_ids: userIds,
    });
    return response.data;
  },

  /**
   * Obtiene la lista de grupos públicos descubribles
   */
  async getDiscoverableGroups(): Promise<Conversation[]> {
    const response = await httpClient.get<Conversation[]>('groups/discover/');
    return response.data;
  },

  /**
   * Envía una solicitud para unirse a un grupo público
   */
  async requestJoinGroup(groupId: number): Promise<void> {
    await httpClient.post(`groups/${groupId}/request_join/`, {});
  },

  /**
   * Elimina permanentemente una conversación
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await httpClient.delete(`conversations/${conversationId}/delete/`);
  },

  /**
   * Carga el historial de mensajes de una conversación
   */
  async getMessages(conversationId: number): Promise<ChatMessage[]> {
    const response = await httpClient.get<ChatMessage[]>(`conversations/${conversationId}/messages/`);
    return response.data;
  },

  /**
   * Marca como leída una conversación
   */
  async markAsRead(conversationId: number): Promise<void> {
    await httpClient.post(`conversations/${conversationId}/read/`, {});
  },

  /**
   * Elimina un mensaje para todos los participantes
   */
  async deleteMessage(messageId: number): Promise<void> {
    await httpClient.delete(`messages/${messageId}/delete/`);
  },

  /**
   * Oculta un mensaje solo para el usuario en sesión
   */
  async hideMessage(messageId: number): Promise<void> {
    await httpClient.post(`messages/${messageId}/hide/`, {});
  },

  /**
   * Sube un archivo adjunto (imagen, video, audio o documento) a la conversación
   */
  async uploadAttachment(conversationId: number, file: File, content?: string): Promise<ChatMessage> {
    const formData = new FormData();
    formData.append('file', file);
    if (content && content.trim()) {
      formData.append('content', content.trim());
    }

    const response = await httpClient.post<ChatMessage>(`conversations/${conversationId}/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Obtiene la lista de usuarios disponibles para añadir a chats/grupos
   */
  async getUsers(): Promise<ChatUser[]> {
    const response = await httpClient.get<ChatUser[]>('users/');
    return response.data;
  },

  /**
   * Obtiene solicitudes pendientes de acceso a grupos administrados
   */
  async getPendingRequests(): Promise<JoinRequest[]> {
    const response = await httpClient.get<JoinRequest[]>('groups/join_requests/');
    return response.data;
  },

  /**
   * Acepta o rechaza una solicitud de unión a grupo
   */
  async manageJoinRequest(requestId: number, action: 'accept' | 'reject'): Promise<void> {
    await httpClient.post(`groups/join_requests/${requestId}/manage/`, { action });
  },

  /**
   * Añade usuarios a un grupo
   */
  async addUsersToGroup(conversationId: number, userIds: number[]): Promise<void> {
    await httpClient.post(`groups/${conversationId}/add_users/`, { user_ids: userIds });
  },
};

export default chatService;
