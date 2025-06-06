'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  mode: 'login' | 'register';
  onSwitchMode: (mode: 'login' | 'register') => void;
}

interface LoginFormData {
  login: string;
  password: string;
  rememberMe: boolean;
}

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export default function AuthModal({ isOpen, onClose, mode, onSwitchMode }: AuthModalProps) {
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loginForm = useForm<LoginFormData>();
  const registerForm = useForm<RegisterFormData>();

  const handleLogin = async (data: LoginFormData) => {
    setLoading(true);
    setError('');
    
    try {
      const success = await login(data.login, data.password, data.rememberMe);
      if (success) {
        onClose();
        loginForm.reset();
      } else {
        setError('Login failed, please check your username/email and password');
      }
    } catch (err) {
      setError('Login failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: RegisterFormData) => {
    if (data.password !== data.confirmPassword) {
      setError('Password confirmation does not match');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const success = await register(
        data.username,
        data.email,
        data.password
      );
      if (success) {
        onClose();
        registerForm.reset();
      } else {
        setError('Registration failed, please check your input');
      }
    } catch (err) {
      setError('Registration failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
    setError('');
    loginForm.reset();
    registerForm.reset();
  };

  const handleSwitchMode = (newMode: 'login' | 'register') => {
    setError('');
    onSwitchMode(newMode);
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {mode === 'login' ? 'Login' : 'Register'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' 
              ? 'Login to your account to post messages and comments' 
              : 'Create a new account to start participating'
            }
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {mode === 'login' ? (
          <div className="space-y-4">
            <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login">Username or Email</Label>
                <Input
                  id="login"
                  type="text"
                  placeholder="Enter username or email"
                  {...loginForm.register('login', { required: true })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter password"
                  {...loginForm.register('password', { required: true })}
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  id="rememberMe"
                  type="checkbox"
                  className="rounded border-gray-300"
                  {...loginForm.register('rememberMe')}
                />
                <Label htmlFor="rememberMe" className="text-sm">
                  Remember me (30 days auto-login)
                </Label>
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Logging in...' : 'Login'}
              </Button>
            </form>

            {/* Switch to register */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600">
                Don&apos;t have an account?{' '}
                <button
                  type="button"
                  onClick={() => handleSwitchMode('register')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Register now
                </button>
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="5-20 alphanumeric characters"
                  {...registerForm.register('username', { 
                    required: true,
                    pattern: /^[a-zA-Z0-9_]{5,20}$/
                  })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter email address"
                  {...registerForm.register('email', { required: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="8-20 chars, uppercase, lowercase, number and special char"
                  {...registerForm.register('password', { 
                    required: true,
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/
                  })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="Enter password again"
                  {...registerForm.register('confirmPassword', { required: true })}
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Registering...' : 'Register'}
              </Button>
            </form>

            {/* Switch to login */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => handleSwitchMode('login')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Login now
                </button>
              </p>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 