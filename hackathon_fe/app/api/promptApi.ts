import axiosInstance from '@/app/lib/axios';
import { Prompt } from '@/app/types/prompt';

export const promptApi = {
  // Lấy tất cả prompts
  getAll: async (): Promise<Prompt[]> => {
    const response = await axiosInstance.get<Prompt[]>('/prompts');
    return response.data;
  },

  // Lấy prompt theo ID
  getById: async (id: string): Promise<Prompt> => {
    const response = await axiosInstance.get<Prompt>(`/prompts/${id}`);
    return response.data;
  },

  // Tạo prompt mới
  create: async (data: Partial<Prompt>): Promise<Prompt> => {
    const response = await axiosInstance.post<Prompt>('/prompts', data);
    return response.data;
  },

  // Cập nhật prompt
  update: async (id: string, data: Partial<Prompt>): Promise<Prompt> => {
    const response = await axiosInstance.put<Prompt>(`/prompts/${id}`, data);
    return response.data;
  },

  // Xóa prompt
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/prompts/${id}`);
  },

  // Tìm kiếm prompts theo tên
  search: async (query: string): Promise<Prompt[]> => {
    const response = await axiosInstance.get<Prompt[]>(`/prompts/search`, {
      params: { q: query },
    });
    return response.data;
  },
};
