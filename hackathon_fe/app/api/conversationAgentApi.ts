import axiosInstance from '@/app/lib/axios';
import { ConversationAgent } from '@/app/types/conversationAgent';

export const conversationAgentApi = {
  // Lấy tất cả agents trong một conversation
  getByConversationId: async (conversationId: string): Promise<ConversationAgent[]> => {
    const response = await axiosInstance.get<ConversationAgent[]>(
      `/conversation-agents/conversation/${conversationId}`
    );
    return response.data;
  },

  // Lấy conversation agent theo ID
  getById: async (id: string): Promise<ConversationAgent> => {
    const response = await axiosInstance.get<ConversationAgent>(`/conversation-agents/${id}`);
    return response.data;
  },

  // Thêm agent vào conversation
  create: async (data: Partial<ConversationAgent>): Promise<ConversationAgent> => {
    const response = await axiosInstance.post<ConversationAgent>('/conversation-agents', data);
    return response.data;
  },

  // Cập nhật conversation agent
  update: async (id: string, data: Partial<ConversationAgent>): Promise<ConversationAgent> => {
    const response = await axiosInstance.put<ConversationAgent>(`/conversation-agents/${id}`, data);
    return response.data;
  },

  // Xóa agent khỏi conversation
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/conversation-agents/${id}`);
  },

  // Set active agent cho conversation
  setActive: async (conversationId: string, agentId: string): Promise<ConversationAgent> => {
    const response = await axiosInstance.post<ConversationAgent>(
      `/conversation-agents/set-active`,
      { conversationId, agentId }
    );
    return response.data;
  },

  // Lấy active agent của conversation
  getActive: async (conversationId: string): Promise<ConversationAgent | null> => {
    const response = await axiosInstance.get<ConversationAgent | null>(
      `/conversation-agents/conversation/${conversationId}/active`
    );
    return response.data;
  },
};
