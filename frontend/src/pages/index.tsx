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
          <title>Wish Wall - Where Dreams Come True</title>
          <meta name="description" content="Share your wishes here: wealth, love, travel, education, health... Let beautiful dreams become reality" />
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
                  ✨ Wish Wall ✨
                </h1>
                <p className="mx-auto max-w-2xl text-xl leading-relaxed text-gray-700">
                  Make your beautiful wishes here, and let them travel to every corner of the universe with starlight
                </p>
              </div>
              
              {/* Wish Categories */}
              <div className="flex flex-wrap gap-3 justify-center mx-auto max-w-3xl">
                {[
                  { text: '💰 Wealth', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
                  { text: '💕 Love', color: 'bg-pink-100 text-pink-800 border-pink-200' },
                  { text: '✈️ Travel', color: 'bg-blue-100 text-blue-800 border-blue-200' },
                  { text: '📚 Education', color: 'bg-green-100 text-green-800 border-green-200' },
                  { text: '🌟 Health', color: 'bg-purple-100 text-purple-800 border-purple-200' },
                  { text: '🏠 Home', color: 'bg-orange-100 text-orange-800 border-orange-200' },
                  { text: '👨‍👩‍👧‍👦 Family', color: 'bg-red-100 text-red-800 border-red-200' },
                  { text: '🎯 Career', color: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
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
                🌙 Every wish deserves to be heard, every hope deserves to be cherished
              </p>
            </div>

            <CreateMessageForm onMessageCreated={handleMessageCreated} />

            <div className="space-y-6">
              <div className="text-center">
                <h2 className="mb-2 text-2xl font-bold text-gray-800">
                  🎋 Wish Tree
                </h2>
                <p className="text-gray-600">
                  Collected <span className="font-semibold text-purple-600">{messages.length}</span> beautiful wishes
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