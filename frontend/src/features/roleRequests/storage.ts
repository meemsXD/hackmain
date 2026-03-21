import type { RoleRequest } from '@/api/types';
import type { UserRole } from '@/app/constants/roles';

const KEY = 'waste_mvp_role_requests';

function read(): RoleRequest[] {
  if (typeof window === 'undefined') {
    return [];
  }
  const raw = localStorage.getItem(KEY);
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as RoleRequest[];
  } catch {
    return [];
  }
}

function write(items: RoleRequest[]) {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.setItem(KEY, JSON.stringify(items));
}

export function loadRoleRequests(): RoleRequest[] {
  return read();
}

export function createRoleRequest(role: UserRole, comment: string): RoleRequest {
  const next: RoleRequest = {
    id: crypto.randomUUID(),
    role,
    comment,
    status: 'PENDING',
    createdAt: new Date().toISOString(),
  };
  const existing = read();
  write([next, ...existing]);
  return next;
}
