import { apiClient } from '@/api/client';
import type {
  CreateProcessorDriverPayload,
  PaginatedResponse,
  ProcessorDriverCard,
  RecyclerOption,
} from '@/api/types';

export async function listAvailableRecyclers(): Promise<RecyclerOption[]> {
  const { data } = await apiClient.get<RecyclerOption[] | PaginatedResponse<RecyclerOption>>('/auth/recyclers');
  if (Array.isArray(data)) {
    return data;
  }
  return data.results ?? [];
}

export async function listProcessorDrivers(recyclerId?: number): Promise<ProcessorDriverCard[]> {
  const { data } = await apiClient.get<ProcessorDriverCard[]>('/auth/processor/drivers', {
    params: recyclerId ? { recycler_id: recyclerId } : undefined,
  });
  return data;
}

export async function createProcessorDriver(payload: CreateProcessorDriverPayload): Promise<ProcessorDriverCard> {
  const { data } = await apiClient.post<ProcessorDriverCard>('/auth/processor/drivers', payload);
  return data;
}

export async function assignProcessorDriver(driverId: number, recyclerId?: number): Promise<void> {
  await apiClient.post(`/auth/processor/drivers/${driverId}/assign`, recyclerId ? { recycler_id: recyclerId } : {});
}

export async function unassignProcessorDriver(driverId: number, recyclerId?: number): Promise<void> {
  await apiClient.delete(`/auth/processor/drivers/${driverId}/assign`, {
    data: recyclerId ? { recycler_id: recyclerId } : {},
  });
}
