import axiosInstance from '@/app/lib/axios';
import { Prompt } from '@/app/types/prompt';

export const promptApi = {
  // POST /prompts/ - Create Prompt
  create: async (data: Partial<Prompt>): Promise<Prompt> => {
    const response = await axiosInstance.post<Prompt>('/prompts/', data);
    return response.data;
  },

  // GET /prompts/ - List Prompts
  getAll: async (): Promise<Prompt[]> => {
    const response = await axiosInstance.get<Prompt[]>('/prompts/');
    return response.data;
  },

  // GET /prompts/{prompt_id} - Get Prompt
  getById: async (promptId: string): Promise<Prompt> => {
    const response = await axiosInstance.get<Prompt>(`/prompts/${promptId}`);
    return response.data;
  },

  // PUT /prompts/{prompt_id} - Update Prompt
  update: async (promptId: string, data: Partial<Prompt>): Promise<Prompt> => {
    const response = await axiosInstance.put<Prompt>(`/prompts/${promptId}`, data);
    return response.data;
  },

  // DELETE /prompts/{prompt_id} - Delete Prompt
  delete: async (promptId: string): Promise<void> => {
    await axiosInstance.delete(`/prompts/${promptId}`);
  },
};
