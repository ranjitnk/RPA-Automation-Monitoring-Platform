import { apiClient } from './apiClient';

export interface AuditLogDTO {
  id: string;
  userId: string;
  action: string;
  resource: string;
  resourceId: string;
  changes?: Record<string, { oldValue: unknown; newValue: unknown }>;
  timestamp: string;
  ipAddress?: string;
  status: 'Success' | 'Failure';
  details?: string;
}

export interface AuditService {
  getAuditLogs(
    page?: number,
    pageSize?: number,
    filters?: Record<string, unknown>
  ): Promise<{ data: AuditLogDTO[]; total: number }>;
  getAuditLogsByUser(userId: string): Promise<AuditLogDTO[]>;
  getAuditLogsByResource(resource: string, resourceId: string): Promise<AuditLogDTO[]>;
  exportAuditLogsToCSV(filters?: Record<string, unknown>): Promise<Blob>;
}

export const auditService: AuditService = {
  getAuditLogs: async (page = 1, pageSize = 50, filters = {}) => {
    return apiClient.get('/audit', { page, pageSize, ...filters });
  },

  getAuditLogsByUser: async (userId: string) => {
    return apiClient.get('/audit', { userId });
  },

  getAuditLogsByResource: async (resource: string, resourceId: string) => {
    return apiClient.get('/audit', { resource, resourceId });
  },

  exportAuditLogsToCSV: async (filters = {}) => {
    const response = await apiClient.get('/audit/export/csv', filters);
    return new Blob([response], { type: 'text/csv' });
  },
};
