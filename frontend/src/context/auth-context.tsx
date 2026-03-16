"use client";

import { createContext, useCallback, useEffect, useState } from "react";
import { User, LoginCredentials, RegisterData, AuthTokens } from "@/lib/types";
import { apiFetch, ApiError } from "@/lib/api-client";
import { API_ROUTES, ROUTES } from "@/lib/constants";
import {
  setTokens,
  clearTokens,
  hasTokens,
  getRefreshToken,
} from "@/lib/auth";
import { useRouter } from "next/navigation";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  updateProfile: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const fetchUser = useCallback(async () => {
    try {
      const userData = await apiFetch<User>(API_ROUTES.PROFILE);
      setUser(userData);
    } catch {
      setUser(null);
      clearTokens();
    }
  }, []);

  useEffect(() => {
    if (hasTokens()) {
      fetchUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, [fetchUser]);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      const tokens = await apiFetch<AuthTokens>(
        API_ROUTES.LOGIN,
        {
          method: "POST",
          body: JSON.stringify(credentials),
        },
        false
      );
      setTokens(tokens);
      await fetchUser();
      router.push(ROUTES.PRODUCTS);
    },
    [fetchUser, router]
  );

  const register = useCallback(
    async (data: RegisterData) => {
      const response = await apiFetch<{ user: User; tokens: AuthTokens }>(
        API_ROUTES.REGISTER,
        {
          method: "POST",
          body: JSON.stringify(data),
        },
        false
      );
      setTokens(response.tokens);
      setUser(response.user);
      router.push(ROUTES.PRODUCTS);
    },
    [router]
  );

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) {
        await apiFetch(API_ROUTES.LOGOUT, {
          method: "POST",
          body: JSON.stringify({ refresh: refreshToken }),
        });
      }
    } catch {
      // Ignore logout errors
    } finally {
      clearTokens();
      setUser(null);
      router.push(ROUTES.LOGIN);
    }
  }, [router]);

  const updateProfile = useCallback(
    async (data: Partial<User>) => {
      const updated = await apiFetch<User>(API_ROUTES.PROFILE, {
        method: "PATCH",
        body: JSON.stringify(data),
      });
      setUser(updated);
    },
    []
  );

  const refreshUser = useCallback(async () => {
    await fetchUser();
  }, [fetchUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateProfile,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
