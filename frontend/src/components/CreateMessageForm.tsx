'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/contexts/AuthContext';
import { Message, messagesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface CreateMessageFormProps {
  onMessageCreated: (message: Message) => void;
}

interface MessageFormData {
  content: string;
}

const wishCategories = [
  { emoji: '💰', text: '发财', placeholder: '希望财运亨通，事业成功...' },
  { emoji: '💕', text: '脱单', placeholder: '愿早日遇到那个对的人...' },
  { emoji: '✈️', text: '旅行', placeholder: '想去看看世界的美好...' },
  { emoji: '📚', text: '学业', placeholder: '祈愿学业有成，考试顺利...' },
  { emoji: '🌟', text: '健康', placeholder: '愿身体健康，家人平安...' },
  { emoji: '🏠', text: '安居', placeholder: '希望有个温馨的家...' },
  { emoji: '👨‍👩‍👧‍👦', text: '家庭', placeholder: '愿家庭和睦，幸福美满...' },
  { emoji: '🎯', text: '事业', placeholder: '希望工作顺利，升职加薪...' },
];

export default function CreateMessageForm({ onMessageCreated }: CreateMessageFormProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [charCount, setCharCount] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const form = useForm<MessageFormData>();

  const handleSubmit = async (data: MessageFormData) => {
    if (!user) {
      setError('请先登录');
      return;
    }

    if (data.content.length < 3 || data.content.length > 200) {
      setError('心愿内容长度必须在3-200字之间');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await messagesApi.create({
        content: data.content,
      });

      if (response.status === 201) {
        onMessageCreated(response.data);
        form.reset();
        setCharCount(0);
        setSelectedCategory('');
      } else {
        setError('许愿失败，请稍后重试');
      }
    } catch (err) {
      setError('许愿失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const content = e.target.value;
    setCharCount(content.length);
    form.setValue('content', content);
  };

  const handleCategorySelect = (category: typeof wishCategories[0]) => {
    setSelectedCategory(category.text);
    form.setValue('content', '');
    setCharCount(0);
    
    // 自动聚焦到文本框
    const textarea = document.getElementById('content') as HTMLTextAreaElement;
    if (textarea) {
      textarea.placeholder = category.placeholder;
      textarea.focus();
    }
  };

  if (!user) {
    return (
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <div className="text-6xl">🌟</div>
            <div>
              <p className="text-gray-600 text-lg mb-2">加入许愿墙</p>
              <p className="text-gray-500 text-sm">登录后就可以许下你的美好心愿了</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-center text-2xl text-gray-800">
          🌠 许下你的心愿
        </CardTitle>
        <p className="text-center text-gray-600 text-sm">
          选择一个类别，写下你的美好愿望
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Wish Categories */}
        <div>
          <Label className="text-sm font-medium text-gray-700 mb-3 block">
            选择心愿类别
          </Label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {wishCategories.map((category) => (
              <button
                key={category.text}
                type="button"
                onClick={() => handleCategorySelect(category)}
                className={`p-3 rounded-lg border-2 transition-all duration-200 text-sm font-medium hover:shadow-md ${
                  selectedCategory === category.text
                    ? 'border-purple-400 bg-purple-50 text-purple-700 shadow-md'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-purple-200 hover:bg-purple-25'
                }`}
              >
                <div className="text-lg mb-1">{category.emoji}</div>
                <div>{category.text}</div>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="content" className="text-sm font-medium text-gray-700">
              ✨ 心愿内容
            </Label>
            <Textarea
              id="content"
              placeholder={
                selectedCategory 
                  ? wishCategories.find(c => c.text === selectedCategory)?.placeholder || "写下你的美好心愿... (3-200字)"
                  : "写下你的美好心愿... (3-200字)"
              }
              className="min-h-[120px] resize-none border-gray-200 focus:border-purple-400 focus:ring-purple-400"
              {...form.register('content', { 
                required: true,
                minLength: 3,
                maxLength: 200,
                onChange: handleContentChange
              })}
            />
            <div className="flex justify-between text-sm">
              <span 
                className={`${
                  charCount < 3 
                    ? 'text-gray-400' 
                    : charCount > 180 
                      ? 'text-red-500' 
                      : charCount > 160 
                        ? 'text-yellow-500' 
                        : 'text-green-600'
                }`}
              >
                {charCount}/200 字
              </span>
              {charCount < 3 && (
                <span className="text-gray-400">至少输入3个字符</span>
              )}
              {charCount > 180 && (
                <span className="text-red-500">
                  {charCount > 200 ? '超出字数限制' : '接近字数限制'}
                </span>
              )}
            </div>
          </div>

          <div className="flex justify-center">
            <Button 
              type="submit" 
              disabled={loading || charCount < 3 || charCount > 200}
              className="px-8 py-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-full font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                  <span>许愿中...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span>🌟</span>
                  <span>许愿</span>
                </div>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
} 