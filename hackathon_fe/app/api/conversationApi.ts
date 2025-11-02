import axiosInstance from '@/app/lib/axios';
import { Conversation } from '@/app/types/conversation';

export const conversationApi = {
  // Lấy tất cả conversations của user
  getByUserId: async (userId: string): Promise<Conversation[]> => {
    const response = await axiosInstance.get<Conversation[]>(`/conversations/user/${userId}`);
    return response.data;
  },

  // Lấy một conversation theo ID
  getById: async (id: string): Promise<Conversation> => {
    const response = await axiosInstance.get<Conversation>(`/conversations/${id}`);
    return response.data;
  },

  // Tạo conversation mới
  create: async (data: Partial<Conversation>): Promise<Conversation> => {
    const response = await axiosInstance.post<Conversation>('/conversations', data);
    return response.data;
  },

  // Cập nhật conversation
  update: async (id: string, data: Partial<Conversation>): Promise<Conversation> => {
    const response = await axiosInstance.put<Conversation>(`/conversations/${id}`, data);
    return response.data;
  },

  // Xóa conversation
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/conversations/${id}`);
  },

  // Share conversation
  share: async (id: string): Promise<{ share_token: string }> => {
    const response = await axiosInstance.post<{ share_token: string }>(`/conversations/${id}/share`);
    return response.data;
  },

  // Unshare conversation
  unshare: async (id: string): Promise<void> => {
    await axiosInstance.post(`/conversations/${id}/unshare`);
  },

  // Lấy conversation theo share token
  getByShareToken: async (shareToken: string): Promise<Conversation> => {
    const response = await axiosInstance.get<Conversation>(`/conversations/shared/${shareToken}`);
    return response.data;
  },

  // Cập nhật summary
  updateSummary: async (id: string, summary: string): Promise<Conversation> => {
    const response = await axiosInstance.patch<Conversation>(`/conversations/${id}/summary`, { summary });
    return response.data;
  },
};
