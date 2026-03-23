import type { BatchQr, WasteBatch } from '@/api/types';

export function getBatchLatestStatus(batch: WasteBatch): string {
  if (batch.current_status) {
    return batch.current_status;
  }
  const latest = batch.statuses[batch.statuses.length - 1];
  return latest?.state ?? 'CREATED';
}

export function getBatchLatestStatusTime(batch: WasteBatch): string | null {
  const latest = batch.statuses[batch.statuses.length - 1];
  return latest?.time ?? null;
}

export function getQrExpiry(qr?: BatchQr | null): string | null {
  if (!qr) {
    return null;
  }
  return qr.expires_at ?? qr.time ?? null;
}
