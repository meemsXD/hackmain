import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, setAccessToken, setRefreshToken } from '@/auth/sessionStore';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api/v1';

type RetryableConfig = InternalAxiosRequestConfig & { _retry?: boolean };
type TokenRefresher = () => Promise<{ access: string; refresh?: string } | null>;
type SessionExpiredHandler = () => void;

let refreshTokens: TokenRefresher | null = null;
let onSessionExpired: SessionExpiredHandler | null = null;
let refreshPromise: Promise<{ access: string; refresh?: string } | null> | null = null;

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 20_000,
});

export const publicClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 20_000,
});

export function configureApiAuth(options: {
  refreshTokens: TokenRefresher;
  onSessionExpired: SessionExpiredHandler;
}) {
  refreshTokens = options.refreshTokens;
  onSessionExpired = options.onSessionExpired;
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = (config.headers ?? {}) as InternalAxiosRequestConfig['headers'];
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as RetryableConfig | undefined;

    if (!originalRequest || status !== 401 || originalRequest._retry || !refreshTokens) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    refreshPromise ||= refreshTokens();

    const refreshed = await refreshPromise.finally(() => {
      refreshPromise = null;
    });

    if (!refreshed?.access) {
      onSessionExpired?.();
      return Promise.reject(error);
    }

    setAccessToken(refreshed.access);
    if (refreshed.refresh) {
      setRefreshToken(refreshed.refresh);
    }

    originalRequest.headers = (originalRequest.headers ?? {}) as RetryableConfig['headers'];
    originalRequest.headers.Authorization = `Bearer ${refreshed.access}`;
    return apiClient.request(originalRequest);
  },
);

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Неизвестная ошибка сети.';
  }

  const data = error.response?.data as Record<string, unknown> | string | undefined;
  if (typeof data === 'string') {
    return data;
  }

  if (data && typeof data === 'object') {
    const entries = Object.entries(data);
    const [firstKey, firstValue] = entries[0] ?? [];
    if (Array.isArray(firstValue) && typeof firstValue[0] === 'string') {
      return `${firstKey}: ${firstValue[0]}`;
    }
    if (typeof firstValue === 'string') {
      return `${firstKey}: ${firstValue}`;
    }
  }

  return 'Не удалось выполнить запрос. Проверьте сеть и повторите.';
}
