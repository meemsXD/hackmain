import { apiClient } from '@/api/client';
import type { Organization, PaginatedResponse } from '@/api/types';

export async function listOrganizations(page = 1): Promise<PaginatedResponse<Organization>> {
  const { data } = await apiClient.get<PaginatedResponse<Organization>>('/organizations/', {
    params: { page },
  });
  return data;
}

export async function createOrganization(payload: Omit<Organization, 'id'>): Promise<Organization> {
  const { data } = await apiClient.post<Organization>('/organizations/', payload);
  return data;
}

export async function updateOrganization(id: number, payload: Partial<Omit<Organization, 'id'>>): Promise<Organization> {
  const { data } = await apiClient.patch<Organization>(`/organizations/${id}/`, payload);
  return data;
}
