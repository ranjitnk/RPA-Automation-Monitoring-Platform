import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';
import { useEnvironmentStore } from '@/stores/environmentStore';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export const apiClient = axios.create({ baseURL });

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  const environmentId = useEnvironmentStore.getState().currentEnvironmentId;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (environmentId) config.headers['X-Environment-Id'] = environmentId;
  return config;
});
