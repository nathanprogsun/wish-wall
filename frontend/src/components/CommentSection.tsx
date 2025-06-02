'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { Comment, commentsApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';

interface CommentSectionProps {
  messageId: string;
  comments: Comment[];
  commentCount: number;
  loading: boolean;
  onCommentAdded: (comment: Comment) => void;
  onRequestLogin?: () => void;
}

interface CommentFormData {
  content: string;
}

interface CommentItemProps {
  comment: Comment;
  messageId: string;
  level: number;
  onReply: (comment: Comment) => void;
  onRequestLogin?: () => void;
}

function CommentItem({ comment, messageId, level, onReply, onRequestLogin }: CommentItemProps) {
  const { user } = useAuth();
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [charCount, setCharCount] = useState(0);

  const form = useForm<CommentFormData>();

  const getUserInitials = (username: string) => {
    // Generate initials from username (first 2 characters)
    return username.slice(0, 2).toUpperCase();
  };

  const getDisplayName = (author: any) => {
    // Use display_name if available, otherwise use username
    return author.display_name || author.username;
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

  const handleReply = async (data: CommentFormData) => {
    if (!user) return;

    setLoading(true);
    try {
      const response = await commentsApi.create({
        message_id: messageId,
        content: data.content,
        parent_id: comment.id,
      });

      if (response.status === 201) {
        onReply(response.data);
        form.reset();
        setCharCount(0);
        setShowReplyForm(false);
      }
    } catch (error) {
      console.error('Failed to create reply:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const content = e.target.value;
    setCharCount(content.length);
    form.setValue('content', content);
  };

  const handleReplyClick = () => {
    if (!user && onRequestLogin) {
      onRequestLogin();
    } else {
      setShowReplyForm(!showReplyForm);
    }
  };

  const marginLeft = Math.min(level * 20, 100);

  return (
    <div className="space-y-3" style={{ marginLeft: `${marginLeft}px` }}>
      <div className="flex items-start space-x-3">
        <Avatar className="flex-shrink-0 w-8 h-8 border border-purple-200">
          <AvatarFallback className="text-xs bg-gradient-to-br from-purple-100 to-pink-100 text-purple-600">
            {getUserInitials(comment.author.username)}
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1 min-w-0">
          <div className="p-3 bg-white rounded-lg border border-purple-100 shadow-sm">
            <div className="flex items-center mb-2 space-x-2">
              <span className="text-sm font-medium text-gray-800">
                {getDisplayName(comment.author)}
              </span>
              <span className="text-xs text-purple-500">🙏</span>
              <span className="text-xs text-gray-500">
                {formatDate(comment.created_at)}
              </span>
            </div>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {comment.content}
            </p>
          </div>
          
          <div className="flex items-center mt-2 space-x-2">
            <Button
              variant="ghost"
              size="sm"
              className="px-2 h-6 text-xs text-purple-600 hover:text-purple-700 hover:bg-purple-50"
              onClick={handleReplyClick}
            >
              💝 {user ? '回复祝福' : '回复祝福'}
            </Button>
          </div>

          {showReplyForm && user && (
            <form onSubmit={form.handleSubmit(handleReply)} className="mt-3 space-y-2">
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-purple-600">
                    回复 @{getDisplayName(comment.author)} 的祝福
                  </span>
                  <span className={`text-xs ${
                    charCount > 200 ? 'text-red-500' : 
                    charCount > 180 ? 'text-yellow-500' : 'text-gray-500'
                  }`}>
                    {charCount}/200
                  </span>
                </div>
                <Textarea
                  placeholder="送上你的祝福..."
                  rows={3}
                  className="text-sm border-purple-200 focus:border-purple-400 focus:ring-purple-400"
                  {...form.register('content', { 
                    required: true,
                    minLength: 3,
                    maxLength: 200,
                    onChange: handleContentChange
                  })}
                />
              </div>
              <div className="flex space-x-2">
                <Button 
                  type="submit" 
                  size="sm" 
                  disabled={loading || charCount < 3 || charCount > 200}
                  className="bg-purple-500 hover:bg-purple-600 text-white"
                >
                  {loading ? '发送中...' : '🌟 发送'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowReplyForm(false)}
                  className="border-purple-200 text-purple-600 hover:bg-purple-50"
                >
                  取消
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>

      {comment.replies && comment.replies.map((child) => (
        <CommentItem
          key={child.id}
          comment={child}
          messageId={messageId}
          level={level + 1}
          onReply={onReply}
          onRequestLogin={onRequestLogin}
        />
      ))}
    </div>
  );
}

export default function CommentSection({ messageId, comments, commentCount, loading, onCommentAdded, onRequestLogin }: CommentSectionProps) {
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [charCount, setCharCount] = useState(0);

  const form = useForm<CommentFormData>();

  const handleSubmit = async (data: CommentFormData) => {
    if (!user) return;

    setSubmitting(true);
    try {
      const response = await commentsApi.create({
        message_id: messageId,
        content: data.content,
      });

      if (response.status === 201) {
        onCommentAdded(response.data);
        form.reset();
        setCharCount(0);
        setShowForm(false);
      }
    } catch (error) {
      console.error('Failed to create comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const content = e.target.value;
    setCharCount(content.length);
    form.setValue('content', content);
  };

  const handleCommentReply = (newComment: Comment) => {
    onCommentAdded(newComment);
  };

  const handleWriteCommentClick = () => {
    if (!user && onRequestLogin) {
      onRequestLogin();
    } else {
      setShowForm(true);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="py-4 text-center">
          <div className="inline-flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full border-b-2 border-purple-600 animate-spin"></div>
            <span className="text-sm text-gray-500">加载祝福中...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Separator className="bg-gradient-to-r from-transparent via-purple-200 to-transparent" />
      
      <div className="flex justify-between items-center">
        <h4 className="font-medium text-gray-800 flex items-center space-x-2">
          <span>💝</span>
          <span>祝福 ({commentCount})</span>
        </h4>
        {!showForm && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleWriteCommentClick}
            className="border-purple-200 text-purple-600 hover:bg-purple-50 hover:border-purple-300"
          >
            🌟 {user ? '写祝福' : '写祝福'}
          </Button>
        )}
      </div>

      {showForm && user && (
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-3">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-purple-700 font-medium">送上你的祝福</span>
              <span className={`text-sm ${
                charCount > 200 ? 'text-red-500' : 
                charCount > 180 ? 'text-yellow-500' : 'text-gray-500'
              }`}>
                {charCount}/200
              </span>
            </div>
            <Textarea
              placeholder="愿这个美好的心愿早日实现..."
              rows={4}
              className="border-purple-200 focus:border-purple-400 focus:ring-purple-400"
              {...form.register('content', { 
                required: true,
                minLength: 3,
                maxLength: 200,
                onChange: handleContentChange
              })}
            />
          </div>
          <div className="flex space-x-2">
            <Button 
              type="submit" 
              size="sm" 
              disabled={submitting || charCount < 3 || charCount > 200}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
            >
              {submitting ? '发送中...' : '✨ 发送祝福'}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowForm(false)}
              className="border-purple-200 text-purple-600 hover:bg-purple-50"
            >
              取消
            </Button>
          </div>
        </form>
      )}

      <div className="space-y-4">
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            messageId={messageId}
            level={0}
            onReply={handleCommentReply}
            onRequestLogin={onRequestLogin}
          />
        ))}
      </div>

      {comments.length === 0 && !loading && (
        <div className="py-8 text-center text-gray-500 space-y-2">
          <div className="text-4xl">🙏</div>
          <p>还没有人送祝福，快来送上第一个祝福吧！</p>
        </div>
      )}
    </div>
  );
} 