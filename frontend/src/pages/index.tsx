import { useState } from 'react';
import { GetServerSideProps } from 'next';
import Head from 'next/head';
import { AuthProvider } from '@/contexts/AuthContext';
import { Message, messagesApi } from '@/lib/api';
import Header from '@/components/Header';
import MessageList from '@/components/MessageList';
import CreateMessageForm from '@/components/CreateMessageForm';
import AuthModal from '@/components/AuthModal';

interface HomeProps {
  initialMessages: Message[];
}

export default function Home({ initialMessages }: HomeProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [loading, setLoading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const handleMessageCreated = (newMessage: Message) => {
    setMessages([newMessage, ...messages]);
  };

  const openAuthModal = (mode: 'login' | 'register' = 'login') => {
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  const handleRequestLogin = () => {
    openAuthModal('login');
  };

  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
        <Head>
          <title>许愿墙 - 心愿成真的地方</title>
          <meta name="description" content="在这里许下你的心愿：发财、脱单、旅行、学业、健康...让美好的愿望照进现实" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <Header onOpenAuth={openAuthModal} />

        <main className="container px-4 py-8 mx-auto max-w-4xl">
          <div className="space-y-8">
            {/* Hero Section */}
            <div className="space-y-6 text-center">
              <div className="space-y-4">
                <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600">
                  ✨ 许愿墙 ✨
                </h1>
                <p className="mx-auto max-w-2xl text-xl leading-relaxed text-gray-700">
                  在这里许下你的美好心愿，愿望会随着星光传递到宇宙的每一个角落
                </p>
              </div>
              
              {/* Wish Categories */}
              <div className="flex flex-wrap gap-3 justify-center mx-auto max-w-3xl">
                {[
                  { text: '💰 发财', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
                  { text: '💕 脱单', color: 'bg-pink-100 text-pink-800 border-pink-200' },
                  { text: '✈️ 旅行', color: 'bg-blue-100 text-blue-800 border-blue-200' },
                  { text: '📚 学业', color: 'bg-green-100 text-green-800 border-green-200' },
                  { text: '🌟 健康', color: 'bg-purple-100 text-purple-800 border-purple-200' },
                  { text: '🏠 安居', color: 'bg-orange-100 text-orange-800 border-orange-200' },
                  { text: '👨‍👩‍👧‍👦 家庭', color: 'bg-red-100 text-red-800 border-red-200' },
                  { text: '🎯 事业', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
                ].map((category) => (
                  <span
                    key={category.text}
                    className={`inline-block px-4 py-2 rounded-full text-sm font-medium border ${category.color} transition-transform hover:scale-105`}
                  >
                    {category.text}
                  </span>
                ))}
              </div>
              
              <p className="text-sm text-gray-600">
                🌙 每一个心愿都值得被聆听，每一份期待都值得被呵护
              </p>
            </div>

            <CreateMessageForm onMessageCreated={handleMessageCreated} />

            <div className="space-y-6">
              <div className="text-center">
                <h2 className="mb-2 text-2xl font-bold text-gray-800">
                  🎋 愿望树
                </h2>
                <p className="text-gray-600">
                  共收集了 <span className="font-semibold text-purple-600">{messages.length}</span> 个美好心愿
                </p>
              </div>
              
              <MessageList
                messages={messages}
                loading={loading}
                onRequestLogin={handleRequestLogin}
              />
            </div>
          </div>
        </main>

        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          mode={authMode}
          onSwitchMode={setAuthMode}
        />
      </div>
    </AuthProvider>
  );
}

export const getServerSideProps: GetServerSideProps = async () => {
  try {
    const response = await messagesApi.getAll();
    
    if (response.status === 200) {
      return {
        props: {
          initialMessages: response.data,
        },
      };
    } else {
      console.error('Failed to fetch messages:', response.error);
      return {
        props: {
          initialMessages: [],
        },
      };
    }
  } catch (error) {
    console.error('Failed to fetch initial messages:', error);
    return {
      props: {
        initialMessages: [],
      },
    };
  }
}; 