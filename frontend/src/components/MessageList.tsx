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
  if (loading) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 3 }).map((_, index) => (
          <div
            key={index}
            className="p-6 w-full rounded-lg border border-gray-200 shadow-sm animate-pulse bg-white/80"
          >
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="w-32 h-4 bg-gray-300 rounded"></div>
                <div className="w-24 h-3 bg-gray-200 rounded"></div>
              </div>
            </div>
            <div className="mt-4 space-y-2">
              <div className="w-full h-4 bg-gray-300 rounded"></div>
              <div className="w-3/4 h-4 bg-gray-300 rounded"></div>
              <div className="w-1/2 h-4 bg-gray-300 rounded"></div>
            </div>
            <div className="flex justify-between items-center mt-4">
              <div className="w-20 h-6 bg-gray-200 rounded"></div>
              <div className="w-16 h-6 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Show empty state when no messages
  if (messages.length === 0) {
    return (
      <div className="py-16 space-y-6 text-center">
        <div className="space-y-4">
          <div className="text-8xl">🌟</div>
          <div className="space-y-2">
            <p className="text-xl font-medium text-gray-600">The wish wall is still empty</p>
            <p className="text-gray-500">Be the first to make a wish! Let the starlight witness your beautiful dreams</p>
          </div>
        </div>
        <div className="flex justify-center space-x-2 text-sm text-gray-400">
          <span>✨</span>
          <span>Every wish deserves to be fulfilled</span>
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
      <div className="py-8 space-y-3 text-center">
        <div className="flex justify-center space-x-2 text-2xl">
          <span className="animate-pulse">⭐</span>
          <span className="delay-100 animate-pulse">🌟</span>
          <span className="delay-200 animate-pulse">✨</span>
          <span className="delay-300 animate-pulse">💫</span>
          <span className="delay-200 animate-pulse">✨</span>
          <span className="delay-100 animate-pulse">🌟</span>
          <span className="animate-pulse">⭐</span>
        </div>
        <p className="text-sm text-gray-500">
          May all beautiful wishes come true 🌙
        </p>
      </div>
    </div>
  );
} 