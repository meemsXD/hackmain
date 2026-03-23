import type { UserRole } from '@/app/constants/roles';

export type Nullable<T> = T | null;

export type DriverProfile = {
  id: number;
  vehicle_number: string;
};

export type EducatorProfile = {
  id: number;
  license_number: string;
  address: string;
};

export type ProcessorProfile = {
  id: number;
  license_number: string;
  facility_address: string;
  drivers: number[];
};

export type RecyclerOption = {
  id: number;
  license_number: string;
  facility_address: string;
  organization_id: number | null;
  organization_name?: string | null;
  user_id?: number | null;
};

export type ProcessorDriverCard = {
  id: number;
  vehicle_number: string;
  user_id?: number;
  user_login?: string;
  user_full_name?: string;
};

export type CreateProcessorDriverPayload = {
  vehicle_number: string;
  full_name?: string;
  login?: string;
  password?: string;
  organization?: number;
};

export type User = {
  id: number;
  login: string;
  full_name: string;
  role: UserRole;
  organization: Nullable<number>;
  driver_profile: Nullable<DriverProfile>;
  educator_profile: Nullable<EducatorProfile>;
  processor_profile: Nullable<ProcessorProfile>;
};

export type LoginPayload = {
  login: string;
  password: string;
};

export type RegisterPayload = {
  login: string;
  full_name: string;
  role: UserRole;
  organization: number | null;
  password: string;
  vehicle_number?: string;
  license_number?: string;
  address?: string;
  facility_address?: string;
};

export type AuthTokens = {
  access: string;
  refresh: string;
};

export type RegisterResponse = {
  user: User;
  access: string;
  refresh: string;
};

export type Organization = {
  id: number;
  inn: string;
  kpp: string;
  name: string;
};

export type BatchStatus = {
  id: number;
  state: string;
  time: string;
  waste: number;
  changed_by?: number | null;
};

export type BatchQr = {
  id: number;
  waste: number;
  code: string;
  is_active: boolean;
  expires_at?: string;
  // Legacy compatibility for older backend snapshots.
  time?: string;
  created_by?: number | null;
  is_expired?: boolean;
};

export type WasteBatch = {
  id: number;
  waste_type: string;
  quantity: string;
  medical_organization: number;
  pickup_point: string;
  delivery_point: number;
  statuses: BatchStatus[];
  qr: Nullable<BatchQr>;
  current_status?: string;
  created_by?: number | null;
};

export type CreateWasteBatchPayload = {
  waste_type: string;
  quantity: string;
  medical_organization: number;
  pickup_point: string;
  delivery_point: number;
  qr_expires_hours?: number;
};

export type UpdateStatusPayload = {
  state: string;
};

export type QrScanPayload = {
  code: string;
};

export type QrScanResponse = {
  batch: WasteBatch;
  qr: BatchQr;
};

export type QrScanLog = {
  id: number;
  qr: number | null;
  raw_code: string;
  scanned_by: number | null;
  scanned_at: string;
  success: boolean;
  fail_reason: string;
};

export type AuditLog = {
  id: number;
  user: number | null;
  user_email: string;
  action: string;
  object_type: string;
  object_id: string;
  before: unknown;
  after: unknown;
  created_at: string;
};

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type RoleRequest = {
  id: string;
  role: UserRole;
  comment: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  createdAt: string;
};

export type ChatMessage = {
  id: string;
  authorName: string;
  authorId: string | null;
  body: string;
  isSystem: boolean;
  createdAt: string;
};
