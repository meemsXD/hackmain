import { apiClient, publicClient } from '@/api/client';
import type {
  BatchQr,
  CreateWasteBatchPayload,
  PaginatedResponse,
  QrScanPayload,
  QrScanResponse,
  QrScanLog,
  UpdateStatusPayload,
  WasteBatch,
} from '@/api/types';

export async function listBatches(page = 1): Promise<PaginatedResponse<WasteBatch>> {
  const { data } = await apiClient.get<PaginatedResponse<WasteBatch>>('/batches/', {
    params: { page },
  });
  return data;
}

export async function listAllBatches(maxPages = 10): Promise<WasteBatch[]> {
  const chunks: WasteBatch[] = [];
  let page = 1;
  let hasNext = true;

  while (hasNext && page <= maxPages) {
    const data = await listBatches(page);
    chunks.push(...data.results);
    hasNext = Boolean(data.next);
    page += 1;
  }

  return chunks;
}

export async function getBatch(id: number | string): Promise<WasteBatch> {
  const { data } = await apiClient.get<WasteBatch>(`/batches/${id}/`);
  return data;
}

export async function createBatch(payload: CreateWasteBatchPayload): Promise<WasteBatch> {
  const { data } = await apiClient.post<WasteBatch>('/batches/', payload);
  return data;
}

export async function updateBatchStatus(id: number | string, payload: UpdateStatusPayload): Promise<{ state: string }> {
  const { data } = await apiClient.post<{ state: string }>(`/batches/${id}/status/`, payload);
  return data;
}

export async function getBatchQr(id: number | string): Promise<BatchQr> {
  const { data } = await apiClient.get<BatchQr>(`/batches/${id}/qr/`);
  return data;
}

export async function scanQrCode(payload: QrScanPayload): Promise<QrScanResponse> {
  const { data } = await publicClient.post<QrScanResponse>('/batches/qr/scan/', payload);
  return data;
}

export async function listBatchQrLogs(id: number | string, blockedOnly = true): Promise<QrScanLog[]> {
  const { data } = await apiClient.get<PaginatedResponse<QrScanLog> | QrScanLog[]>(`/batches/${id}/qr/logs/`, {
    params: { blocked: blockedOnly ? 1 : 0 },
  });
  return Array.isArray(data) ? data : data.results;
}

export async function extendBatchQr(id: number | string, hours: number): Promise<BatchQr> {
  const { data } = await apiClient.post<BatchQr>(`/batches/${id}/qr/extend/`, { hours });
  return data;
}
