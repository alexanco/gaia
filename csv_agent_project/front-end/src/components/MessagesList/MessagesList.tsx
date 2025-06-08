import React, { useEffect, useRef } from 'react';
import { User, Bot, Sparkles, Brain, Zap, Copy } from 'lucide-react';
import { Message, AIModel } from '../../pages/Home/Home';
import * as S from './styles';

interface MessagesListProps {
  messages: Message[];
  selectedModel: AIModel;
  isLoading: boolean;
}

const MessagesList: React.FC<MessagesListProps> = ({
  messages,
  selectedModel,
  isLoading
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const models = {
    claude: { name: 'Claude', icon: Bot, color: '#16a34a' },
    deepseek: { name: 'DeepSeek', icon: Brain, color: '#15803d' },
    gemini: { name: 'Gemini', icon: Sparkles, color: '#166534' },
    openai: { name: 'GPT-4', icon: Zap, color: '#22c55e' }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const copyMessage = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <S.Container>
      {messages.map(message => {
        const isUser = message.sender === 'user';
        const modelInfo = models[selectedModel];
        const IconComponent = isUser ? User : modelInfo.icon;

        return (
          <S.MessageContainer key={message.id} $isUser={isUser}>
            <S.MessageBubble $isUser={isUser} $color={modelInfo.color}>
              <S.MessageHeader>
                <S.MessageSender>
                  <IconComponent size={16} />
                  <span>{isUser ? 'Você' : message.model}</span>
                </S.MessageSender>
                <S.MessageTime>{formatTime(message.timestamp)}</S.MessageTime>
              </S.MessageHeader>
              <S.MessageText>{message.text}</S.MessageText>
              {!isUser && (
                <S.CopyButton onClick={() => copyMessage(message.text)}>
                  <Copy size={14} />
                </S.CopyButton>
              )}
            </S.MessageBubble>
          </S.MessageContainer>
        );
      })}
      
      {isLoading && (
        <S.MessageContainer $isUser={false}>
          <S.LoadingBubble $color={models[selectedModel].color}>
            <S.LoadingDots>
              <div></div>
              <div></div>
              <div></div>
            </S.LoadingDots>
            <span>{models[selectedModel].name} está pensando...</span>
          </S.LoadingBubble>
        </S.MessageContainer>
      )}
      
      <div ref={messagesEndRef} />
    </S.Container>
  );
};

export default MessagesList;