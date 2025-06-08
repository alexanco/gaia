import React, { useState, useEffect } from 'react';
import Header from '../../components/Header/Header';
import Sidebar from '../../components/Sidebar/Sidebar';
import ChatArea from '../../components/ChatArea/ChatArea';
import * as S from './styles';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  model: string;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export type AIModel = 'claude' | 'deepseek' | 'gemini' | 'openai';

const Home: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<AIModel>('claude');
  const [sidebarOpen, setSidebarOpen] = useState(false); // Inicia fechado no mobile

  const activeChat = chats.find(chat => chat.id === activeChatId);

  // Fechar sidebar quando trocar de chat no mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setSidebarOpen(true);
      } else {
        setSidebarOpen(false);
      }
    };

    // Configurar estado inicial baseado no tamanho da tela
    handleResize();
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const createNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: 'Nova Conversa',
      messages: [],
      createdAt: new Date()
    };
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    
    // Fechar sidebar no mobile após criar chat
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const deleteChat = (chatId: string) => {
    setChats(prev => prev.filter(chat => chat.id !== chatId));
    if (activeChatId === chatId) {
      setActiveChatId(null);
    }
  };

  const updateChat = (updatedChat: Chat) => {
    setChats(prev => {
      const existingChatIndex = prev.findIndex(chat => chat.id === updatedChat.id);
      
      if (existingChatIndex >= 0) {
        // Chat já existe, atualizar
        return prev.map(chat => 
          chat.id === updatedChat.id ? updatedChat : chat
        );
      } else {
        // Novo chat, adicionar e selecionar
        setActiveChatId(updatedChat.id);
        return [updatedChat, ...prev];
      }
    });
  };

  const handleChatSelect = (chatId: string) => {
    setActiveChatId(chatId);
    
    // Fechar sidebar no mobile após selecionar chat
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <S.Container>
      {/* Overlay para mobile */}
      {sidebarOpen && <S.Overlay onClick={() => setSidebarOpen(false)} />}
      
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        sidebarOpen={sidebarOpen}
        onChatSelect={handleChatSelect}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
      />
      
      <S.MainContent>
        <Header
          activeChat={activeChat}
          selectedModel={selectedModel}
          sidebarOpen={sidebarOpen}
          onModelChange={setSelectedModel}
          onToggleSidebar={toggleSidebar}
        />
        
        <ChatArea
          activeChat={activeChat}
          selectedModel={selectedModel}
          onUpdateChat={updateChat}
          onCreateChat={createNewChat}
        />
      </S.MainContent>
    </S.Container>
  );
};

export default Home;