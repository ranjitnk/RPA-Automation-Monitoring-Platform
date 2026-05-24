import { apiClient } from './apiClient';

export interface RobotDTO {
  id: number;
  name: string;
  machineId?: number;
  machineName?: string;
  type: 'Attended' | 'Unattended' | 'NonProduction';
  enabled: boolean;
  status: 'Available' | 'Unavailable' | 'Executing';
  username?: string;
  executionSessions: number;
  licenseKey?: string;
  version?: string;
  heartbeatTime?: string;
  jobsCompleted: number;
  jobsFailed: number;
}

export interface RobotsService {
  getRobots(page?: number, pageSize?: number, filters?: Record<string, unknown>): Promise<{ data: RobotDTO[]; total: number }>;
  getRobotById(id: number): Promise<RobotDTO>;
  getRobotsByType(type: string): Promise<RobotDTO[]>;
  getRobotStats(): Promise<Record<string, number>>;
  exportRobotsToCSV(): Promise<Blob>;
}

export const robotsService: RobotsService = {
  getRobots: async (page = 1, pageSize = 20, filters = {}) => {
    return apiClient.get('/robots', { page, pageSize, ...filters });
  },

  getRobotById: async (id: number) => {
    return apiClient.get(`/robots/${id}`);
  },

  getRobotsByType: async (type: string) => {
    return apiClient.get('/robots', { type });
  },

  getRobotStats: async () => {
    return apiClient.get('/robots/stats');
  },

  exportRobotsToCSV: async () => {
    const response = await apiClient.get('/robots/export/csv');
    return new Blob([response], { type: 'text/csv' });
  },
};
