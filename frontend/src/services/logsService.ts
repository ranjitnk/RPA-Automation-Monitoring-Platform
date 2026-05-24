import { apiClient } from './apiClient';

export interface LogEntryDTO {
  id: string;
  jobId: number;
  timestamp: string;
  level: 'Debug' | 'Info' | 'Warning' | 'Error';
  message: string;
  source?: string;
  details?: Record<string, unknown>;
}

export interface LogsService {
  getLogs(
    page?: number,
    pageSize?: number,
    filters?: Record<string, unknown>
  ): Promise<{ data: LogEntryDTO[]; total: number }>;
  getLogsByJob(jobId: number): Promise<LogEntryDTO[]>;
  searchLogs(query: string, page?: number, pageSize?: number): Promise<{ data: LogEntryDTO[]; total: number }>;
  exportLogsToCSV(filters?: Record<string, unknown>): Promise<Blob>;
}

export const logsService: LogsService = {
  getLogs: async (page = 1, pageSize = 50, filters = {}) => {
    return apiClient.get('/logs', { page, pageSize, ...filters });
  },

  getLogsByJob: async (jobId: number) => {
    return apiClient.get(`/logs/job/${jobId}`);
  },

  searchLogs: async (query: string, page = 1, pageSize = 50) => {
    return apiClient.get('/logs/search', { q: query, page, pageSize });
  },

  exportLogsToCSV: async (filters = {}) => {
    const response = await apiClient.get('/logs/export/csv', filters);
    return new Blob([response], { type: 'text/csv' });
  },
};
