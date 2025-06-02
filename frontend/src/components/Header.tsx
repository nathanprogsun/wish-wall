'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

interface HeaderProps {
  onOpenAuth: (mode: 'login' | 'register') => void;
}

export default function Header({ onOpenAuth }: HeaderProps) {
  const { user, logout } = useAuth();

  const getUserInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-purple-100 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 max-w-4xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              ✨ 许愿墙
            </h1>
            <span className="text-sm text-gray-500 hidden sm:block">
              心愿成真的地方
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <Avatar className="w-8 h-8 border border-purple-200">
                    <AvatarFallback className="text-xs bg-gradient-to-br from-purple-100 to-pink-100 text-purple-600">
                      {getUserInitials(user.username)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm text-gray-700 hidden sm:block">
                    {user.display_name || user.username}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="border-purple-200 text-purple-600 hover:bg-purple-50 hover:border-purple-300"
                >
                  退出
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onOpenAuth('login')}
                  className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                >
                  登录
                </Button>
                <Button
                  size="sm"
                  onClick={() => onOpenAuth('register')}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
                >
                  注册
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
} 