import axiosInstance from '@/app/lib/axios';
import { SharedConversation } from '@/app/types/sharedConversation';

export const sharedConversationApi = {
  // POST /shared-conversations/ - Create Shared Conversation
  create: async (data: Partial<SharedConversation>): Promise<SharedConversation> => {
    const response = await axiosInstance.post<SharedConversation>('/shared-conversations/', data);
    return response.data;
  },

  // GET /shared-conversations/ - Get All Shared Conversations
  getAll: async (): Promise<SharedConversation[]> => {
    const response = await axiosInstance.get<SharedConversation[]>('/shared-conversations/');
    return response.data;
  },

  // GET /shared-conversations/{shared_conv_id} - Get Shared Conversation
  getById: async (sharedConvId: string): Promise<SharedConversation> => {
    const response = await axiosInstance.get<SharedConversation>(`/shared-conversations/${sharedConvId}`);
    return response.data;
  },

  // PUT /shared-conversations/{shared_conv_id} - Update Shared Conversation
  update: async (sharedConvId: string, data: Partial<SharedConversation>): Promise<SharedConversation> => {
    const response = await axiosInstance.put<SharedConversation>(
      `/shared-conversations/${sharedConvId}`,
      data
    );
    return response.data;
  },

  // DELETE /shared-conversations/{shared_conv_id} - Delete Shared Conversation
  delete: async (sharedConvId: string): Promise<void> => {
    await axiosInstance.delete(`/shared-conversations/${sharedConvId}`);
  },

  // GET /shared-conversations/conversation/{conversation_id} - Get Shared Conversations By Conversation
  getByConversationId: async (conversationId: string): Promise<SharedConversation[]> => {
    const response = await axiosInstance.get<SharedConversation[]>(
      `/shared-conversations/conversation/${conversationId}`
    );
    return response.data;
  },

  // DELETE /shared-conversations/conversation/{conversation_id} - Delete Shared Conversations By Conversation
  deleteByConversationId: async (conversationId: string): Promise<void> => {
    await axiosInstance.delete(`/shared-conversations/conversation/${conversationId}`);
  },

  // GET /shared-conversations/user/{user_id} - Get Shared Conversations By User
  getByUserId: async (userId: string): Promise<SharedConversation[]> => {
    const response = await axiosInstance.get<SharedConversation[]>(
      `/shared-conversations/user/${userId}`
    );
    return response.data;
  },

  // POST /shared-conversations/share/{conversation_id}/to/{user_id} - Share Conversation To User
  shareToUser: async (conversationId: string, userId: string): Promise<SharedConversation> => {
    const response = await axiosInstance.post<SharedConversation>(
      `/shared-conversations/share/${conversationId}/to/${userId}`
    );
    return response.data;
  },
};
