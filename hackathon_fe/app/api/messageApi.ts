import axiosInstance from '@/app/lib/axios';
import { Message } from '@/app/types/message';

export const messageApi = {
  // Lấy tất cả messages trong một conversation
  getByConversationId: async (conversationId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/conversation/${conversationId}`);
    return response.data;
  },

  // Lấy một message theo ID
  getById: async (id: string): Promise<Message> => {
    const response = await axiosInstance.get<Message>(`/messages/${id}`);
    return response.data;
  },

  // Tạo message mới
  create: async (data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.post<Message>('/messages', data);
    return response.data;
  },

  // Cập nhật message
  update: async (id: string, data: Partial<Message>): Promise<Message> => {
    const response = await axiosInstance.put<Message>(`/messages/${id}`, data);
    return response.data;
  },

  // Xóa message
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/messages/${id}`);
  },

  // Cập nhật reaction
  updateReaction: async (id: string, reaction: string): Promise<Message> => {
    const response = await axiosInstance.patch<Message>(`/messages/${id}/reaction`, { reaction });
    return response.data;
  },

  // Lấy messages theo user
  getByUserId: async (userId: string): Promise<Message[]> => {
    const response = await axiosInstance.get<Message[]>(`/messages/user/${userId}`);
    return response.data;
  },
};
