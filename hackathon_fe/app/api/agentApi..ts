import axiosInstance from '@/app/lib/axios';
import { Agent } from '@/app/types/agent';

export const agentApi = {
  // Lấy tất cả agents
  getAll: async (): Promise<Agent[]> => {
    const response = await axiosInstance.get<Agent[]>('/agents');
    return response.data;
  },

  // Lấy agent theo ID
  getById: async (id: string): Promise<Agent> => {
    const response = await axiosInstance.get<Agent>(`/agents/${id}`);
    return response.data;
  },

  // Tạo agent mới
  create: async (data: Partial<Agent>): Promise<Agent> => {
    const response = await axiosInstance.post<Agent>('/agents', data);
    return response.data;
  },

  // Cập nhật agent
  update: async (id: string, data: Partial<Agent>): Promise<Agent> => {
    const response = await axiosInstance.put<Agent>(`/agents/${id}`, data);
    return response.data;
  },

  // Xóa agent
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/agents/${id}`);
  },

  // Lấy agents theo provider
  getByProvider: async (provider: string): Promise<Agent[]> => {
    const response = await axiosInstance.get<Agent[]>(`/agents/provider/${provider}`);
    return response.data;
  },

  // Lấy active agents
  getActive: async (): Promise<Agent[]> => {
    const response = await axiosInstance.get<Agent[]>('/agents/active');
    return response.data;
  },
};
