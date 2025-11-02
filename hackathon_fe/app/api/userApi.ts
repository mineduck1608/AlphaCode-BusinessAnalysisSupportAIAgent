import axiosInstance from '@/app/lib/axios';
import { User } from '@/app/types/user';

export const userApi = {
  // Lấy thông tin user hiện tại
  getCurrentUser: async (): Promise<User> => {
    const response = await axiosInstance.get<User>('/users/me');
    return response.data;
  },

  // Lấy user theo ID
  getById: async (id: string): Promise<User> => {
    const response = await axiosInstance.get<User>(`/users/${id}`);
    return response.data;
  },

  // Lấy tất cả users (admin only)
  getAll: async (): Promise<User[]> => {
    const response = await axiosInstance.get<User[]>('/users');
    return response.data;
  },

  // Tạo user mới
  create: async (data: Partial<User>): Promise<User> => {
    const response = await axiosInstance.post<User>('/users', data);
    return response.data;
  },

  // Cập nhật user
  update: async (id: string, data: Partial<User>): Promise<User> => {
    const response = await axiosInstance.put<User>(`/users/${id}`, data);
    return response.data;
  },

  // Xóa user
  delete: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/users/${id}`);
  },

  // Đổi mật khẩu
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await axiosInstance.post('/users/change-password', { oldPassword, newPassword });
  },

  // Login
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const response = await axiosInstance.post<{ token: string; user: User }>('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Register
  register: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const response = await axiosInstance.post<{ token: string; user: User }>('/auth/register', {
      email,
      password,
    });
    return response.data;
  },

  // Logout
  logout: async (): Promise<void> => {
    await axiosInstance.post('/auth/logout');
  },
};
