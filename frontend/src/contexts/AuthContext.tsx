'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, authApi } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (login: string, password: string, rememberMe?: boolean) => Promise<boolean>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // Use the new initializeAuth method that handles JWT tokens
      const userData = await authApi.initializeAuth();
      setUser(userData);
    } catch (error) {
      console.log('Failed to initialize auth:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (login: string, password: string, rememberMe = false): Promise<boolean> => {
    try {
      const loginResponse = await authApi.login({ login, password, remember_me: rememberMe });
      if (loginResponse.status === 200) {
        // JWT tokens are already stored in the login method
        // Now fetch the user profile
        try {
          const profileResponse = await authApi.getProfile();
          if (profileResponse.status === 200) {
            setUser(profileResponse.data);
            return true;
          } else {
            // If profile fetch fails but login succeeded, use user data from login response
            if (loginResponse.data && loginResponse.data.user) {
              setUser(loginResponse.data.user);
              return true;
            }
          }
        } catch (profileError) {
          console.error('Failed to fetch profile after login:', profileError);
          // Use user data from login response as fallback
          if (loginResponse.data && loginResponse.data.user) {
            setUser(loginResponse.data.user);
            return true;
          }
        }
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      // Always clear user state, even if logout request fails
      setUser(null);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string
  ): Promise<boolean> => {
    try {
      const response = await authApi.register({
        username,
        email,
        password,
      });
      if (response.status === 201) {
        // Auto login after registration
        return await login(username, password);
      }
      return false;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    register,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 