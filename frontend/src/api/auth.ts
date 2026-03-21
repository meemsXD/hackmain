import { apiClient, publicClient } from '@/api/client';
import type { AuthTokens, LoginPayload, RegisterPayload, RegisterResponse, User } from '@/api/types';

export async function login(payload: LoginPayload): Promise<AuthTokens> {
  const { data } = await publicClient.post<AuthTokens>('/auth/login', payload);
  return data;
}

export async function register(payload: RegisterPayload): Promise<RegisterResponse | AuthTokens> {
  const { data } = await publicClient.post<RegisterResponse | AuthTokens>('/auth/register', payload);
  return data;
}

export async function me(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
}

export async function refresh(payload: { refresh: string }): Promise<AuthTokens> {
  const { data } = await publicClient.post<AuthTokens>('/auth/refresh', payload);
  return data;
}

export async function logout(payload: { refresh: string }): Promise<void> {
  await apiClient.post('/auth/logout', payload);
}
