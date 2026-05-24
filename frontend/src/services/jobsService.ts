import { apiClient } from './apiClient';

export interface JobDTO {
  id: number;
  name: string;
  releaseId?: number;
  robotId?: number;
  status: 'Running' | 'Completed' | 'Failed' | 'Stopped' | 'Pending';
  state: string;
  createdTime: string;
  startTime?: string;
  endTime?: string;
  duration?: number;
  inputArguments?: Record<string, unknown>;
  outputArguments?: Record<string, unknown>;
}

export interface JobsService {
  getJobs(
    page?: number,
    pageSize?: number,
    filters?: Record<string, unknown>
  ): Promise<{ data: JobDTO[]; total: number }>;
  getJobById(id: number): Promise<JobDTO>;
  getJobsByRobot(robotId: number): Promise<JobDTO[]>;
  getJobsByStatus(status: string): Promise<JobDTO[]>;
  exportJobsToCSV(filters?: Record<string, unknown>): Promise<Blob>;
}

export const jobsService: JobsService = {
  getJobs: async (page = 1, pageSize = 20, filters = {}) => {
    return apiClient.get('/jobs', {
      ...filters,
      page,
      pageSize,
    });
  },

  getJobById: async (id: number) => {
    return apiClient.get(`/jobs/${id}`);
  },

  getJobsByRobot: async (robotId: number) => {
    return apiClient.get(`/jobs/robot/${robotId}`);
  },

  getJobsByStatus: async (status: string) => {
    return apiClient.get('/jobs', { status });
  },

  exportJobsToCSV: async (filters = {}) => {
    const response = await apiClient.get(`/jobs/export/csv`, {
      ...filters,
      format: 'csv',
    });
    return new Blob([response], { type: 'text/csv' });
  },
};
