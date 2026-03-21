import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';
import { configureApiAuth, getApiErrorMessage } from '@/api/client';
import { login as loginApi, logout as logoutApi, me, refresh, register as registerApi } from '@/api/auth';
import type { LoginPayload, RegisterPayload, User } from '@/api/types';
import {
  clearSessionTokens,
  clearStoredUser,
  getRefreshToken,
  getSignatureToken,
  getStoredUser,
  setSessionTokens,
  setSignatureToken,
  setStoredUser,
} from '@/auth/sessionStore';
import { getUserRoles } from '@/utils/roles';
import type { UserRole } from '@/app/constants/roles';

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated' | 'forbidden' | 'session_expired';

type AuthContextValue = {
  user: User | null;
  roles: UserRole[];
  status: AuthStatus;
  error: string | null;
  signatureToken: string;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  saveSignatureToken: (token: string) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function clearAllSession() {
  clearSessionTokens();
  clearStoredUser();
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(() => getStoredUser());
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [error, setError] = useState<string | null>(null);
  const [signatureToken, setSignatureTokenState] = useState<string>(() => getSignatureToken());

  const hydrateUser = useCallback(async () => {
    const currentUser = await me();
    setUser(currentUser);
    setStoredUser(currentUser);
    const roles = getUserRoles(currentUser);
    setStatus(roles.length ? 'authenticated' : 'forbidden');
  }, []);

  const refreshTokens = useCallback(async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      return null;
    }
    try {
      const next = await refresh({ refresh: refreshToken });
      setSessionTokens(next.access, next.refresh || refreshToken);
      return { access: next.access, refresh: next.refresh || refreshToken };
    } catch {
      return null;
    }
  }, []);

  const handleSessionExpired = useCallback(() => {
    clearAllSession();
    setUser(null);
    setStatus('session_expired');
  }, []);

  const bootstrap = useCallback(async () => {
    setStatus('loading');
    setError(null);
    const refreshed = await refreshTokens();
    if (!refreshed) {
      setStatus('unauthenticated');
      return;
    }
    try {
      await hydrateUser();
    } catch (err) {
      clearAllSession();
      setStatus('unauthenticated');
      setError(getApiErrorMessage(err));
    }
  }, [hydrateUser, refreshTokens]);

  useEffect(() => {
    configureApiAuth({
      refreshTokens,
      onSessionExpired: handleSessionExpired,
    });
  }, [handleSessionExpired, refreshTokens]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      setError(null);
      const tokens = await loginApi(payload);
      setSessionTokens(tokens.access, tokens.refresh);
      await hydrateUser();
    },
    [hydrateUser],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      setError(null);
      const response = await registerApi(payload);
      if ('user' in response) {
        setSessionTokens(response.access, response.refresh);
        setUser(response.user);
        setStoredUser(response.user);
        setStatus(getUserRoles(response.user).length ? 'authenticated' : 'forbidden');
        return;
      }
      setSessionTokens(response.access, response.refresh);
      await hydrateUser();
    },
    [hydrateUser],
  );

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await logoutApi({ refresh: refreshToken });
      } catch {
        // Backend может вернуть 401/500 на logout, но сессию все равно очищаем.
      }
    }
    clearAllSession();
    setUser(null);
    setStatus('unauthenticated');
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      await hydrateUser();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  }, [hydrateUser]);

  const saveSignatureToken = useCallback((token: string) => {
    setSignatureTokenState(token);
    setSignatureToken(token);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      roles: getUserRoles(user),
      status,
      error,
      signatureToken,
      login,
      register,
      logout,
      refreshUser,
      saveSignatureToken,
    }),
    [error, login, logout, refreshUser, register, signatureToken, status, user, saveSignatureToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext должен использоваться внутри AuthProvider');
  }
  return context;
}
