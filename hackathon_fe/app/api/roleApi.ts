import axiosInstance from '@/app/lib/axios';
import { Role } from '@/app/types/role';

export const roleApi = {
  // POST /roles/ - Create Role
  create: async (data: Partial<Role>): Promise<Role> => {
    const response = await axiosInstance.post<Role>('/roles/', data);
    return response.data;
  },

  // GET /roles/ - List Roles
  getAll: async (): Promise<Role[]> => {
    const response = await axiosInstance.get<Role[]>('/roles/');
    return response.data;
  },

  // GET /roles/{role_id} - Get Role
  getById: async (roleId: string): Promise<Role> => {
    const response = await axiosInstance.get<Role>(`/roles/${roleId}`);
    return response.data;
  },

  // PUT /roles/{role_id} - Update Role
  update: async (roleId: string, data: Partial<Role>): Promise<Role> => {
    const response = await axiosInstance.put<Role>(`/roles/${roleId}`, data);
    return response.data;
  },

  // DELETE /roles/{role_id} - Delete Role
  delete: async (roleId: string): Promise<void> => {
    await axiosInstance.delete(`/roles/${roleId}`);
  },
};
