import React from 'react';
import { Bot, Plus, MessageSquare, Trash2 } from 'lucide-react';
import { Chat } from '../../pages/Home/Home';
import * as S from './styles';

interface SidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  sidebarOpen: boolean;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  activeChatId,
  sidebarOpen,
  onChatSelect,
  onNewChat,
  onDeleteChat
}) => {
  const handleDeleteChat = (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteChat(chatId);
  };

  return (
    <S.Container $isOpen={sidebarOpen}>
      <S.Header>
        <S.Logo>
          <Bot size={24} />
          <span>Gaia AI</span>
        </S.Logo>
        <S.NewChatButton onClick={onNewChat}>
          <Plus size={18} />
          <span>Nova Conversa</span>
        </S.NewChatButton>
      </S.Header>
      
      <S.ChatList>
        {chats.map(chat => (
          <S.ChatItem 
            key={chat.id}
            $isActive={chat.id === activeChatId}
            onClick={() => onChatSelect(chat.id)}
          >
            <MessageSquare size={16} />
            <S.ChatInfo>
              <S.ChatTitle>{chat.title}</S.ChatTitle>
              <S.ChatPreview>
                {chat.messages.length > 0 
                  ? `${chat.messages[chat.messages.length - 1].text.slice(0, 40)}...`
                  : 'Conversa vazia'
                }
              </S.ChatPreview>
            </S.ChatInfo>
            <S.DeleteButton onClick={(e) => handleDeleteChat(chat.id, e)}>
              <Trash2 size={14} />
            </S.DeleteButton>
          </S.ChatItem>
        ))}
      </S.ChatList>
    </S.Container>
  );
};

export default Sidebar;