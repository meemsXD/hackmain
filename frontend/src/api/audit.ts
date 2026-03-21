import { apiClient } from '@/api/client';
import type { AuditLog, PaginatedResponse } from '@/api/types';

export async function listAuditLogs(page = 1): Promise<PaginatedResponse<AuditLog>> {
  const { data } = await apiClient.get<PaginatedResponse<AuditLog>>('/audit/', {
    params: { page },
  });
  return data;
}
