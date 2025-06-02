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
        setError('登录失败，请检查用户名/邮箱和密码');
      }
    } catch (err) {
      setError('登录失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: RegisterFormData) => {
    if (data.password !== data.confirmPassword) {
      setError('密码确认不匹配');
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
        setError('注册失败，请检查输入信息');
      }
    } catch (err) {
      setError('注册失败，请稍后重试');
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
            {mode === 'login' ? '登录' : '注册'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' 
              ? '登录到你的账户以发表留言和评论' 
              : '创建新账户开始参与讨论'
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
                <Label htmlFor="login">用户名或邮箱</Label>
                <Input
                  id="login"
                  type="text"
                  placeholder="输入用户名或邮箱"
                  {...loginForm.register('login', { required: true })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="输入密码"
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
                  记住我（30天内免登录）
                </Label>
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? '登录中...' : '登录'}
              </Button>
            </form>

            {/* Switch to register */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600">
                还没有账户？{' '}
                <button
                  type="button"
                  onClick={() => handleSwitchMode('register')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  立即注册
                </button>
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="5-20位字母数字组合"
                  {...registerForm.register('username', { 
                    required: true,
                    pattern: /^[a-zA-Z0-9_]{5,20}$/
                  })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">邮箱</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="输入邮箱地址"
                  {...registerForm.register('email', { required: true })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="8-20位，包含大小写字母、数字和特殊符号"
                  {...registerForm.register('password', { 
                    required: true,
                    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/
                  })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">确认密码</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="再次输入密码"
                  {...registerForm.register('confirmPassword', { required: true })}
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? '注册中...' : '注册'}
              </Button>
            </form>

            {/* Switch to login */}
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600">
                已有账户？{' '}
                <button
                  type="button"
                  onClick={() => handleSwitchMode('login')}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  立即登录
                </button>
              </p>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 