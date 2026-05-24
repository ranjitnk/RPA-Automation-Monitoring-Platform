import { apiClient } from './apiClient';

export interface AIMetricsDTO {
  id: string;
  workflowId: number;
  workflowName: string;
  accuracy: number;
  confidence: number;
  processingTime: number;
  errorRate: number;
  anomalyScore: number;
  status: 'Normal' | 'Degraded' | 'Anomaly';
  lastUpdated: string;
  performance: {
    precision: number;
    recall: number;
    f1Score: number;
  };
}

export interface AIMonitoringService {
  getAIMetrics(page?: number, pageSize?: number): Promise<{ data: AIMetricsDTO[]; total: number }>;
  getAIMetricsById(id: string): Promise<AIMetricsDTO>;
  getAIMetricsHistory(id: string): Promise<AIMetricsDTO[]>;
  getAnomalies(): Promise<AIMetricsDTO[]>;
}

export const aiMonitoringService: AIMonitoringService = {
  getAIMetrics: async (page = 1, pageSize = 20) => {
    return apiClient.get('/ai-monitoring', { page, pageSize });
  },

  getAIMetricsById: async (id: string) => {
    return apiClient.get(`/ai-monitoring/${id}`);
  },

  getAIMetricsHistory: async (id: string) => {
    return apiClient.get(`/ai-monitoring/${id}/history`);
  },

  getAnomalies: async () => {
    return apiClient.get('/ai-monitoring/anomalies');
  },
};
