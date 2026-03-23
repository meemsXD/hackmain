import type { User } from '@/api/types';

const REFRESH_KEY = 'waste_mvp_refresh';
const USER_KEY = 'waste_mvp_user';
const SIGNATURE_KEY = 'waste_mvp_signature_token';

let accessTokenInMemory = '';

function readStorage(key: string): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return localStorage.getItem(key) ?? '';
}

function writeStorage(key: string, value: string): void {
  if (typeof window === 'undefined') {
    return;
  }
  if (!value) {
    localStorage.removeItem(key);
    return;
  }
  localStorage.setItem(key, value);
}

export function getAccessToken(): string {
  return accessTokenInMemory;
}

export function setAccessToken(token: string): void {
  accessTokenInMemory = token;
}

export function getRefreshToken(): string {
  return readStorage(REFRESH_KEY);
}

export function setRefreshToken(token: string): void {
  writeStorage(REFRESH_KEY, token);
}

export function setSessionTokens(access: string, refresh: string): void {
  setAccessToken(access);
  setRefreshToken(refresh);
}

export function clearSessionTokens(): void {
  accessTokenInMemory = '';
  writeStorage(REFRESH_KEY, '');
}

export function setStoredUser(user: User | null): void {
  writeStorage(USER_KEY, user ? JSON.stringify(user) : '');
}

export function getStoredUser(): User | null {
  const raw = readStorage(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function clearStoredUser(): void {
  writeStorage(USER_KEY, '');
}

export function setSignatureToken(value: string): void {
  writeStorage(SIGNATURE_KEY, value);
}

export function getSignatureToken(): string {
  return readStorage(SIGNATURE_KEY);
}

export function clearSignatureToken(): void {
  writeStorage(SIGNATURE_KEY, '');
}
