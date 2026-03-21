export type UserRole = 'RECYCLER' | 'DRIVER' | 'MEDICAL' | 'INSPECTOR' | 'ADMIN';

export const ROLE_LABELS: Record<UserRole, string> = {
  RECYCLER: 'Образователь',
  DRIVER: 'Водитель',
  MEDICAL: 'Переработчик',
  INSPECTOR: 'Инспектор',
  ADMIN: 'Администратор',
};

export const ROLE_HOME_PATH: Record<UserRole, string> = {
  RECYCLER: '/app/educator/batches',
  DRIVER: '/app/driver/batches',
  MEDICAL: '/app/processor/batches',
  INSPECTOR: '/app/inspector/journal',
  ADMIN: '/app/profile',
};

export const STATUS_LABELS: Record<string, string> = {
  CREATED: 'Создана',
  IN_TRANSIT: 'В пути',
  DELIVERED: 'Доставлена',
  ACCEPTED: 'Принята',
  CANCELLED: 'Отменена',
  TOKEN_EXPIRED: 'Токен истек',
};

export const STATUS_FLOW = ['CREATED', 'IN_TRANSIT', 'DELIVERED', 'ACCEPTED', 'CANCELLED'] as const;
