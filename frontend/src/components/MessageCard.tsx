'use client';

import { useState, useEffect } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { Message, Comment, messagesApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import CommentSection from '@/components/CommentSection';

interface MessageCardProps {
  message: Message;
  onRequestLogin?: () => void;
}

export default function MessageCard({ message, onRequestLogin }: MessageCardProps) {
  const { user } = useAuth();
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<Comment[]>(message.comments || []);
  const [commentCount, setCommentCount] = useState(message.comment_count);
  const [loadingComments, setLoadingComments] = useState(false);

  const getUserInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  const getWishIcon = (messageId: string) => {
    // 使用消息ID生成确定性图标，避免hydration错误
    const icons = ['🌟', '✨', '💫', '⭐', '🌠', '💝', '🎋', '🌙'];
    const hash = messageId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return icons[hash % icons.length];
  };

  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), {
        addSuffix: true,
        locale: zhCN,
      });
    } catch {
      return '刚刚';
    }
  };

  const handleToggleComments = async () => {
    if (!showComments) {
      // 展开评论时，重新获取最新的message数据以确保嵌套结构正确
      setLoadingComments(true);
      try {
        const response = await messagesApi.getById(message.id);
        if (response.status === 200 && response.data.comments) {
          setComments(response.data.comments);
          setCommentCount(response.data.comment_count);
        }
      } catch (error) {
        console.error('Failed to fetch message details:', error);
      } finally {
        setLoadingComments(false);
      }
    }
    setShowComments(!showComments);
  };

  const handleCommentAdded = async (newComment: Comment) => {
    // 当新评论添加后，重新获取完整的message数据以确保嵌套结构正确
    try {
      setLoadingComments(true);
      const response = await messagesApi.getById(message.id);
      if (response.status === 200) {
        setComments(response.data.comments || []);
        setCommentCount(response.data.comment_count);
      }
    } catch (error) {
      console.error('Failed to refresh comments:', error);
      // 如果重新获取失败，fallback到简单的添加方式
      setComments([newComment, ...comments]);
      setCommentCount(commentCount + 1);
    } finally {
      setLoadingComments(false);
    }
  };

  const handleAddCommentClick = () => {
    if (!user && onRequestLogin) {
      onRequestLogin();
    } else {
      setShowComments(true);
    }
  };

  return (
    <Card className="w-full border-0 shadow-lg backdrop-blur-sm transition-all duration-300 bg-white/90 hover:shadow-xl">
      <CardHeader className="pb-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <Avatar className="w-12 h-12 border-2 border-purple-200">
              <AvatarFallback className="font-semibold text-purple-700 bg-gradient-to-br from-purple-100 to-pink-100">
                {getUserInitials(message.author.username)}
              </AvatarFallback>
            </Avatar>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center mb-1 space-x-2">
              <span className="text-lg">{getWishIcon(message.id)}</span>
              <div className="font-semibold text-gray-800">
                {message.author.display_name || message.author.username}
              </div>
              <span className="text-sm text-gray-500">许了一个愿</span>
            </div>
            <div className="text-sm text-gray-500">
              {formatDate(message.created_at)}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-4">
          <div className="relative">
            <div className="absolute top-0 -left-2 text-3xl text-purple-200 opacity-50">&ldquo;</div>
            <p className="py-2 pr-6 pl-6 italic text-gray-700 whitespace-pre-wrap bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-l-4 border-purple-300">
              {message.content}
            </p>
            <div className="absolute bottom-0 -right-2 text-3xl text-purple-200 opacity-50 rotate-180">&rdquo;</div>
          </div>

          <Separator className="bg-gradient-to-r from-transparent via-purple-200 to-transparent" />

          <div className="flex justify-between items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleToggleComments}
              className="text-purple-600 transition-colors hover:text-purple-700 hover:bg-purple-50"
              disabled={loadingComments}
            >
              <span className="mr-2">💭</span>
              {loadingComments ? '加载中...' : showComments ? '收起祝福' : `查看祝福 (${commentCount})`}
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleAddCommentClick}
              className="text-purple-600 border-purple-200 transition-colors hover:bg-purple-50 hover:border-purple-300"
            >
              <span className="mr-1">🙏</span>
              {user ? '送祝福' : '送祝福'}
            </Button>
          </div>

          {showComments && (
            <div className="p-4 mt-4 bg-gradient-to-r rounded-lg from-purple-50/50 to-pink-50/50">
              <CommentSection
                messageId={message.id}
                comments={comments}
                commentCount={commentCount}
                loading={loadingComments}
                onCommentAdded={handleCommentAdded}
                onRequestLogin={onRequestLogin}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 