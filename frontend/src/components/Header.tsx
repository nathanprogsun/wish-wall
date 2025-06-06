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
    <header className="sticky top-0 z-50 border-b border-purple-100 shadow-sm backdrop-blur-sm bg-white/80">
      <div className="container px-4 py-4 mx-auto max-w-4xl">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">
              ✨ Wish Wall
            </h1>
            <span className="hidden text-sm text-gray-500 sm:block">
              Where Dreams Come True
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <Avatar className="w-8 h-8 border border-purple-200">
                    <AvatarFallback className="text-xs text-purple-600 bg-gradient-to-br from-purple-100 to-pink-100">
                      {getUserInitials(user.username)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden text-sm text-gray-700 sm:block">
                    {user.display_name || user.username}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                  className="text-purple-600 border-purple-200 hover:bg-purple-50 hover:border-purple-300"
                >
                  Logout
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
                  Login
                </Button>
                <Button
                  size="sm"
                  onClick={() => onOpenAuth('register')}
                  className="text-white bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                >
                  Register
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
} 