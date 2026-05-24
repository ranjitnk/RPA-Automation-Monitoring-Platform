import { apiClient } from './apiClient';

export interface AlertDTO {
  id: string;
  title: string;
  description: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';
  status: 'New' | 'Acknowledged' | 'Resolved';
  source: string;
  sourceId?: number;
  createdTime: string;
  resolvedTime?: string;
  metadata?: Record<string, unknown>;
}

export interface AlertsService {
  getAlerts(page?: number, pageSize?: number, filters?: Record<string, unknown>): Promise<{ data: AlertDTO[]; total: number }>;
  getAlertById(id: string): Promise<AlertDTO>;
  acknowledgeAlert(id: string): Promise<void>;
  resolveAlert(id: string): Promise<void>;
  getAlertStats(): Promise<Record<string, number>>;
}

export const alertsService: AlertsService = {
  getAlerts: async (page = 1, pageSize = 20, filters = {}) => {
    return apiClient.get('/alerts', { page, pageSize, ...filters });
  },

  getAlertById: async (id: string) => {
    return apiClient.get(`/alerts/${id}`);
  },

  acknowledgeAlert: async (id: string) => {
    await apiClient.put(`/alerts/${id}/acknowledge`, {});
  },

  resolveAlert: async (id: string) => {
    await apiClient.put(`/alerts/${id}/resolve`, {});
  },

  getAlertStats: async () => {
    return apiClient.get('/alerts/stats');
  },
};
