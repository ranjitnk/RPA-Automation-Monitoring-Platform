import { apiClient } from './apiClient';

export interface QueueDTO {
  id: number;
  name: string;
  maxRetries: number;
  acceptOrphanedItems: boolean;
  createdTime: string;
  itemCount: number;
  processingCount: number;
  failedCount: number;
  successCount: number;
}

export interface QueueItemDTO {
  id: string;
  queueId: number;
  status: 'New' | 'In Progress' | 'Successful' | 'Failed' | 'Retrying';
  priority: number;
  dueDate?: string;
  createdTime: string;
  startTime?: string;
  endTime?: string;
  retryNumber: number;
  specificData?: Record<string, unknown>;
}

export interface QueuesService {
  getQueues(page?: number, pageSize?: number): Promise<{ data: QueueDTO[]; total: number }>;
  getQueueById(id: number): Promise<QueueDTO>;
  getQueueItems(queueId: number, page?: number, pageSize?: number): Promise<{ data: QueueItemDTO[]; total: number }>;
  getQueueStats(): Promise<Record<string, number>>;
  exportQueueToCSV(queueId: number): Promise<Blob>;
}

export const queuesService: QueuesService = {
  getQueues: async (page = 1, pageSize = 20) => {
    return apiClient.get('/queues', { page, pageSize });
  },

  getQueueById: async (id: number) => {
    return apiClient.get(`/queues/${id}`);
  },

  getQueueItems: async (queueId: number, page = 1, pageSize = 20) => {
    return apiClient.get(`/queues/${queueId}/items`, { page, pageSize });
  },

  getQueueStats: async () => {
    return apiClient.get('/queues/stats');
  },

  exportQueueToCSV: async (queueId: number) => {
    const response = await apiClient.get(`/queues/${queueId}/export/csv`);
    return new Blob([response], { type: 'text/csv' });
  },
};
