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
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Try to get profile using session cookies
      const response = await authApi.getProfile();
      if (response.status === 200 && response.data) {
        setUser(response.data);
      } else if (response.status === 401 || response.status === 403) {
        // Authentication failed - user not logged in
        setUser(null);
      } else {
        // Other error responses
        console.log('Failed to fetch user profile:', response.error);
        setUser(null);
      }
    } catch (error: any) {
      // Handle network errors or other exceptions
      console.log('No active session - user not logged in');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (login: string, password: string, rememberMe = false): Promise<boolean> => {
    try {
      const loginResponse = await authApi.login({ login, password, remember_me: rememberMe });
      if (loginResponse.status === 200) {
        // After successful login, fetch complete user profile
        try {
          const profileResponse = await authApi.getProfile();
          if (profileResponse.status === 200) {
            setUser(profileResponse.data);
            return true;
          }
        } catch (profileError) {
          console.error('Failed to fetch profile after login:', profileError);
          // Even if profile fetch fails, login was successful
          // Use the user data from login response as fallback
          setUser(loginResponse.data);
          return true;
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