'use client';

import { Message } from '@/lib/api';
import MessageCard from '@/components/MessageCard';

interface MessageListProps {
  messages: Message[];
  loading: boolean;
  onRequestLogin?: () => void;
}

export default function MessageList({ messages, loading, onRequestLogin }: MessageListProps) {
  // Show loading skeleton when initially loading
  if (loading && messages.length === 0) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="p-6 bg-white/80 rounded-lg border shadow-lg">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-purple-200 rounded-full"></div>
                <div className="space-y-2">
                  <div className="w-32 h-4 bg-purple-200 rounded"></div>
                  <div className="w-20 h-3 bg-gray-200 rounded"></div>
                </div>
              </div>
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="w-4/5 h-4 bg-gray-200 rounded"></div>
                <div className="w-3/5 h-4 bg-gray-200 rounded"></div>
              </div>
              <div className="flex items-center mt-6 space-x-4">
                <div className="w-20 h-6 bg-purple-200 rounded"></div>
                <div className="w-16 h-6 bg-purple-200 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Show empty state when no messages
  if (messages.length === 0) {
    return (
      <div className="py-16 text-center space-y-6">
        <div className="space-y-4">
          <div className="text-8xl">🌟</div>
          <div className="space-y-2">
            <p className="text-xl text-gray-600 font-medium">愿望墙还很空呢</p>
            <p className="text-gray-500">成为第一个许愿的人吧！让星光见证你的美好心愿</p>
          </div>
        </div>
        <div className="flex justify-center space-x-2 text-sm text-gray-400">
          <span>✨</span>
          <span>每一个心愿都值得被实现</span>
          <span>✨</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <MessageCard
          key={message.id}
          message={message}
          onRequestLogin={onRequestLogin}
        />
      ))}
      
      {/* Bottom decoration */}
      <div className="text-center py-8 space-y-3">
        <div className="flex justify-center space-x-2 text-2xl">
          <span className="animate-pulse">⭐</span>
          <span className="animate-pulse delay-100">🌟</span>
          <span className="animate-pulse delay-200">✨</span>
          <span className="animate-pulse delay-300">💫</span>
          <span className="animate-pulse delay-200">✨</span>
          <span className="animate-pulse delay-100">🌟</span>
          <span className="animate-pulse">⭐</span>
        </div>
        <p className="text-gray-500 text-sm">
          愿所有美好的心愿都能成真 🌙
        </p>
      </div>
    </div>
  );
} 