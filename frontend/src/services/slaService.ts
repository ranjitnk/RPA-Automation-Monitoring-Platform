import { apiClient } from './apiClient';

export interface SLAMetricsDTO {
  id: string;
  processName: string;
  successRate: number;
  averageProcessingTime: number;
  targetTime: number;
  currentStatus: 'On Track' | 'At Risk' | 'Breached';
  startDate: string;
  endDate: string;
  totalJobs: number;
  successfulJobs: number;
  failedJobs: number;
}

export interface SLAService {
  getSLAMetrics(page?: number, pageSize?: number): Promise<{ data: SLAMetricsDTO[]; total: number }>;
  getSLAById(id: string): Promise<SLAMetricsDTO>;
  getSLAHistory(id: string): Promise<SLAMetricsDTO[]>;
  getSLAStats(): Promise<Record<string, number>>;
}

export const slaService: SLAService = {
  getSLAMetrics: async (page = 1, pageSize = 20) => {
    return apiClient.get('/sla', { page, pageSize });
  },

  getSLAById: async (id: string) => {
    return apiClient.get(`/sla/${id}`);
  },

  getSLAHistory: async (id: string) => {
    return apiClient.get(`/sla/${id}/history`);
  },

  getSLAStats: async () => {
    return apiClient.get('/sla/stats');
  },
};
