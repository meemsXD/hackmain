import { ROLE_HOME_PATH, type UserRole } from '@/app/constants/roles';
import type { User } from '@/api/types';

export function getUserRoles(user: User | null): UserRole[] {
  if (!user?.role) {
    return [];
  }
  return [user.role];
}

export function getDefaultHomePath(roles: UserRole[]): string {
  if (!roles.length) {
    return '/app/profile';
  }
  return ROLE_HOME_PATH[roles[0]];
}
