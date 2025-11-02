import axiosInstance from '@/app/lib/axios';
import { SharedConversation } from '@/app/types/sharedConversation';

export const sharedConversationApi = {
  // Lấy tất cả shared conversations của user
  getByUserId: async (userId: string): Promise<SharedConversation[]> => {
    const response = await axiosInstance.get<SharedConversation[]>(
      `/shared-conversations/user/${userId}`
    );
    return response.data;
  },

  // Lấy shared conversation theo ID
  getById: async (id: string): Promise<SharedConversation> => {
    const response = await axiosInstance.get<SharedConversation>(`/shared-conversations/${id}`);
    return response.data;
  },

  // Lấy shared conversations theo conversation ID
  getByConversationId: async (conversationId: string): Promise<SharedConversation[]> => {
    const response = await axiosInstance.get<SharedConversation[]>(
      `/shared-conversations/conversation/${conversationId}`
    );
    return response.data;
  },

  // Tạo shared conversation mới
  create: async (data: Partial<SharedConversation>): Promise<SharedConversation> => {
    const response = await axiosInstance.post<SharedConversation>('/shared-conversations', data);
    return response.data;
  },

  // Xóa shared conversation
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/shared-conversations/${id}`);
  },

  // Revoke share access
  revokeAccess: async (conversationId: string, userId: string): Promise<void> => {
    await axiosInstance.post(`/shared-conversations/revoke`, {
      conversationId,
      userId,
    });
  },
};
