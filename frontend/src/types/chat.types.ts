/**
 * Chat Domain Models & Types
 * Philosophy: Gentleman Programming (Strict typing, explicit domain contracts)
 */

export type AttachmentType = 'image' | 'video' | 'audio' | 'document';

export interface ChatUser {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  profile_picture_url?: string;
}

export interface ChatMessage {
  id: number;
  content: string;
  sender: ChatUser;
  timestamp: string;
  attachment?: string | null;
  attachment_name?: string | null;
  attachment_type?: AttachmentType | null;
}

export interface Conversation {
  id: number;
  name?: string | null;
  is_group: boolean;
  admin?: number | null;
  participants: ChatUser[];
  last_message?: ChatMessage | null;
  unread_count?: number;
  created_at?: string;
}

export interface JoinRequest {
  id: number;
  conversation: number;
  user: ChatUser;
  created_at: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface UploadAttachmentPayload {
  conversationId: number;
  file: File;
  content?: string;
}

export interface WebSocketMessagePayload {
  action?: string;
  message_id?: number;
  id?: number;
  message?: string;
  content?: string;
  sender?: string | ChatUser;
  timestamp?: string;
  attachment?: string | null;
  attachment_name?: string | null;
  attachment_type?: AttachmentType | null;
}
