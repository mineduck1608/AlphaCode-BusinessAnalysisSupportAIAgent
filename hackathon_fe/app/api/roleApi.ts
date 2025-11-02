import axiosInstance from '@/app/lib/axios';
import { Role } from '@/app/types/role';

export const roleApi = {
  // Lấy tất cả roles
  getAll: async (): Promise<Role[]> => {
    const response = await axiosInstance.get<Role[]>('/roles');
    return response.data;
  },

  // Lấy role theo ID
  getById: async (id: string): Promise<Role> => {
    const response = await axiosInstance.get<Role>(`/roles/${id}`);
    return response.data;
  },

  // Tạo role mới
  create: async (data: Partial<Role>): Promise<Role> => {
    const response = await axiosInstance.post<Role>('/roles', data);
    return response.data;
  },

  // Cập nhật role
  update: async (id: string, data: Partial<Role>): Promise<Role> => {
    const response = await axiosInstance.put<Role>(`/roles/${id}`, data);
    return response.data;
  },

  // Xóa role
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/roles/${id}`);
  },
};
