import axiosInstance from '@/app/lib/axios';
import { Conversation } from '@/app/types/conversation';

export const conversationApi = {
  // POST /conversations/ - Create Conversation
  create: async (data: Partial<Conversation>): Promise<Conversation> => {
    const response = await axiosInstance.post<Conversation>('/conversations/', data);
    return response.data;
  },

  // GET /conversations/ - List Conversations
  getAll: async (): Promise<Conversation[]> => {
    const response = await axiosInstance.get<Conversation[]>('/conversations/');
    return response.data;
  },

  // GET /conversations/{conversation_id} - Get Conversation
  getById: async (conversationId: string): Promise<Conversation> => {
    const response = await axiosInstance.get<Conversation>(`/conversations/${conversationId}`);
    return response.data;
  },

  // PUT /conversations/{conversation_id} - Update Conversation
  update: async (conversationId: string, data: Partial<Conversation>): Promise<Conversation> => {
    const response = await axiosInstance.put<Conversation>(`/conversations/${conversationId}`, data);
    return response.data;
  },

  // DELETE /conversations/{conversation_id} - Delete Conversation
  delete: async (conversationId: string): Promise<void> => {
    await axiosInstance.delete(`/conversations/${conversationId}`);
  },

  // POST /conversations/{conversation_id}/agents - Add Agent To Conversation
  addAgent: async (conversationId: string, agentData: { agent_id: string }): Promise<any> => {
    const response = await axiosInstance.post(`/conversations/${conversationId}/agents`, agentData);
    return response.data;
  },

  // GET /conversations/{conversation_id}/agents - List Conversation Agents
  getAgents: async (conversationId: string): Promise<any[]> => {
    const response = await axiosInstance.get(`/conversations/${conversationId}/agents`);
    return response.data;
  },

  // PUT /conversations/agents/{ca_id} - Update Conversation Agent
  updateAgent: async (caId: string, data: any): Promise<any> => {
    const response = await axiosInstance.put(`/conversations/agents/${caId}`, data);
    return response.data;
  },

  // DELETE /conversations/agents/{ca_id} - Delete Conversation Agent
  deleteAgent: async (caId: string): Promise<void> => {
    await axiosInstance.delete(`/conversations/agents/${caId}`);
  },
};
