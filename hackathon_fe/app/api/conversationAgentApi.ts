import axiosInstance from '@/app/lib/axios';
import { ConversationAgent } from '@/app/types/conversationAgent';

export const conversationAgentApi = {
  // POST /conversation-agents/{conversation_id}/agents - Create Conversation Agent
  create: async (conversationId: string, data: Partial<ConversationAgent>): Promise<ConversationAgent> => {
    const response = await axiosInstance.post<ConversationAgent>(
      `/conversation-agents/${conversationId}/agents`,
      data
    );
    return response.data;
  },

  // GET /conversation-agents/{ca_id} - Get Conversation Agent
  getById: async (caId: string): Promise<ConversationAgent> => {
    const response = await axiosInstance.get<ConversationAgent>(`/conversation-agents/${caId}`);
    return response.data;
  },

  // PUT /conversation-agents/{ca_id} - Update Conversation Agent
  update: async (caId: string, data: Partial<ConversationAgent>): Promise<ConversationAgent> => {
    const response = await axiosInstance.put<ConversationAgent>(
      `/conversation-agents/${caId}`,
      data
    );
    return response.data;
  },

  // DELETE /conversation-agents/{ca_id} - Delete Conversation Agent
  delete: async (caId: string): Promise<void> => {
    await axiosInstance.delete(`/conversation-agents/${caId}`);
  },

  // GET /conversation-agents/conversation/{conversation_id} - List By Conversation
  getByConversationId: async (conversationId: string): Promise<ConversationAgent[]> => {
    const response = await axiosInstance.get<ConversationAgent[]>(
      `/conversation-agents/conversation/${conversationId}`
    );
    return response.data;
  },

  // GET /conversation-agents/agent/{agent_id} - List By Agent
  getByAgentId: async (agentId: string): Promise<ConversationAgent[]> => {
    const response = await axiosInstance.get<ConversationAgent[]>(
      `/conversation-agents/agent/${agentId}`
    );
    return response.data;
  },

  // GET /conversation-agents/conversation/{conversation_id}/active - List Active Agents
  getActiveAgents: async (conversationId: string): Promise<ConversationAgent[]> => {
    const response = await axiosInstance.get<ConversationAgent[]>(
      `/conversation-agents/conversation/${conversationId}/active`
    );
    return response.data;
  },

  // POST /conversation-agents/conversation/{conversation_id}/switch/{agent_id} - Switch Active Agent
  switchActiveAgent: async (conversationId: string, agentId: string): Promise<ConversationAgent> => {
    const response = await axiosInstance.post<ConversationAgent>(
      `/conversation-agents/conversation/${conversationId}/switch/${agentId}`
    );
    return response.data;
  },
};
