import axiosInstance from '@/app/lib/axios';
import { Message } from '@/app/types/message';

export const messageApi = {
  // POST /messages/ - Create Message
  create: async (data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.post<Message>('/messages/', data);
    return response.data;
  },

  // GET /messages/ - Get All Messages
  getAll: async (): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>('/messages/');
    return response.data;
  },

  // POST /messages/user - Create User Message
  createUserMessage: async (data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.post<Message>('/messages/user', data);
    return response.data;
  },

  // POST /messages/agent - Create Agent Message
  createAgentMessage: async (data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.post<Message>('/messages/agent', data);
    return response.data;
  },

  // GET /messages/{message_id} - Get Message
  getById: async (messageId: string): Promise<Message> => {
    const response = await axiosInstance.get<Message>(`/messages/${messageId}`);
    return response.data;
  },

  // PUT /messages/{message_id} - Update Message
  update: async (messageId: string, data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.put<Message>(`/messages/${messageId}`, data);
    return response.data;
  },

  // DELETE /messages/{message_id} - Delete Message
  delete: async (messageId: string): Promise<void> => {
    await axiosInstance.delete(`/messages/${messageId}`);
  },

  // GET /messages/conversation/{conversation_id} - Get Conversation Messages
  getByConversationId: async (conversationId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/conversation/${conversationId}`);
    return response.data;
  },

  // DELETE /messages/conversation/{conversation_id} - Delete Conversation Messages
  deleteByConversationId: async (conversationId: string): Promise<void> => {
    await axiosInstance.delete(`/messages/conversation/${conversationId}`);
  },

  // GET /messages/shared-conversation/{shared_conv_id} - Get Shared Conversation Messages
  getBySharedConversationId: async (sharedConvId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/shared-conversation/${sharedConvId}`);
    return response.data;
  },

  // DELETE /messages/shared-conversation/{shared_conv_id} - Delete Shared Conversation Messages
  deleteBySharedConversationId: async (sharedConvId: string): Promise<void> => {
    await axiosInstance.delete(`/messages/shared-conversation/${sharedConvId}`);
  },

  // GET /messages/user/{user_id} - Get User Messages
  getByUserId: async (userId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/user/${userId}`);
    return response.data;
  },

  // GET /messages/agent/{agent_id} - Get Agent Messages
  getByAgentId: async (agentId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/agent/${agentId}`);
    return response.data;
  },

  // PATCH /messages/{message_id}/reaction - Update Message Reaction
  updateReaction: async (messageId: string, reaction: string): Promise<Message> => {
    const response = await axiosInstance.patch<Message>(`/messages/${messageId}/reaction`, { reaction });
    return response.data;
  },

  // GET /messages/conversation/{conversation_id}/with-relations - Get Conversation With Relations
  getConversationWithRelations: async (conversationId: string): Promise<any> => {
    const response = await axiosInstance.get(`/messages/conversation/${conversationId}/with-relations`);
    return response.data;
  },

  // GET /messages/conversation/{conversation_id}/statistics - Get Conversation Statistics
  getConversationStatistics: async (conversationId: string): Promise<any> => {
    const response = await axiosInstance.get(`/messages/conversation/${conversationId}/statistics`);
    return response.data;
  },
};
