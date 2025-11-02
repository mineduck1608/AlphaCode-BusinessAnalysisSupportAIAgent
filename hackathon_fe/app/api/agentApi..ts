import axiosInstance from '@/app/lib/axios';
import { Agent } from '@/app/types/agent';

export const agentApi = {
  // POST /agents/ - Create Agent
  create: async (data: Partial<Agent>): Promise<Agent> => {
    const response = await axiosInstance.post<Agent>('/agents/', data);
    return response.data;
  },

  // GET /agents/ - List Agents
  getAll: async (): Promise<Agent[]> => {
    const response = await axiosInstance.get<Agent[]>('/agents/');
    return response.data;
  },

  // GET /agents/{agent_id} - Get Agent
  getById: async (agentId: string): Promise<Agent> => {
    const response = await axiosInstance.get<Agent>(`/agents/${agentId}`);
    return response.data;
  },

  // PUT /agents/{agent_id} - Update Agent
  update: async (agentId: string, data: Partial<Agent>): Promise<Agent> => {
    const response = await axiosInstance.put<Agent>(`/agents/${agentId}`, data);
    return response.data;
  },

  // DELETE /agents/{agent_id} - Delete Agent
  delete: async (agentId: string): Promise<void> => {
    await axiosInstance.delete(`/agents/${agentId}`);
  },
};
