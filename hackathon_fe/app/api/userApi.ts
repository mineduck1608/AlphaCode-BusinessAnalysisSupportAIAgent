import axiosInstance from '@/app/lib/axios';
import { User } from '@/app/types/user';

export const userApi = {
  // POST /users/login - Login or create user (parameters as query params)
  login: async (email: string, password: string, role_id: number = 1): Promise<User> => {
    const response = await axiosInstance.post<User>("/users/login", null, {
      params: {
        email,
        password,
        role_id,
      },
    });
    return response.data;
  },

  // POST /users/ - Create User
  create: async (data: Partial<User>): Promise<User> => {
    const response = await axiosInstance.post<User>('/users/', data);
    return response.data;
  },

  // GET /users/ - List Users
  getAll: async (): Promise<User[]> => {
    const response = await axiosInstance.get<User[]>('/users/');
    return response.data;
  },

  // GET /users/{user_id} - Get User
  getById: async (userId: string): Promise<User> => {
    const response = await axiosInstance.get<User>(`/users/${userId}`);
    return response.data;
  },

  // PUT /users/{user_id} - Update User
  update: async (userId: string, data: Partial<User>): Promise<User> => {
    const response = await axiosInstance.put<User>(`/users/${userId}`, data);
    return response.data;
  },

  // DELETE /users/{user_id} - Delete User
  delete: async (userId: string): Promise<void> => {
    await axiosInstance.delete(`/users/${userId}`);
  },
};
