import React, { useState } from 'react';
import WelcomeScreen from '../WelcomeScreen/WelcomeScreen';
import MessagesList from '../MessagesList/MessagesList';
import ChatInput from '../ChatInput/ChatInput';
import { Chat, Message, AIModel } from '../../pages/Home/Home';
import * as S from './styles';

interface ChatAreaProps {
  activeChat: Chat | undefined;
  selectedModel: AIModel;
  onUpdateChat: (chat: Chat) => void;
  onCreateChat: () => void;
}

const ChatArea: React.FC<ChatAreaProps> = ({
  activeChat,
  selectedModel,
  onUpdateChat,
}) => {
  const [isLoading, setIsLoading] = useState(false);

  const models = {
    claude: { name: 'Claude', company: 'Anthropic' },
    deepseek: { name: 'DeepSeek', company: 'DeepSeek' },
    gemini: { name: 'Gemini', company: 'Google' },
    openai: { name: 'GPT-4', company: 'OpenAI' }
  };

  const getMockResponse = (userMessage: string, model: AIModel): string => {
    const responses = {
      claude: [
        `Como Claude da Anthropic, analisei sua mensagem sobre "${userMessage.slice(0, 30)}..." e posso oferecer insights detalhados. Minha abordagem prioriza precisão e considerações éticas.`,
        `Interessante questão! Como assistente da Anthropic, vou elaborar uma resposta thoughtful considerando múltiplas perspectivas sobre seu tópico.`,
        `Entendo perfeitamente sua solicitação. Deixe-me fornecer uma análise abrangente usando meu treinamento da Anthropic.`
      ],
      deepseek: [
        `Processando via arquitetura DeepSeek... Sua consulta sobre "${userMessage.slice(0, 30)}..." ativa meus módulos de raciocínio avançado. Aqui está minha análise técnica:`,
        `Como modelo DeepSeek, aplico reasoning profundo para sua questão. Minha arquitetura permite insights únicos através de processamento multinível.`,
        `Excelente! Utilizando capacidades DeepSeek de análise avançada, posso decompor sua questão em componentes técnicos fundamentais.`
      ],
      gemini: [
        `Como Gemini do Google, posso processar sua solicitação multimodalmente. Sobre "${userMessage.slice(0, 30)}...", vou integrar informações de múltiplas fontes.`,
        `Fascinante! Minha arquitetura Gemini permite abordar isso considerando contexto amplo e capacidades multimodais do ecossistema Google.`,
        `Perfeito! Como modelo Google Gemini, tenho acesso a processamento avançado para fornecer respostas abrangentes e contextualizadas.`
      ],
      openai: [
        `Como GPT-4 da OpenAI, processarei sua mensagem "${userMessage.slice(0, 30)}..." usando minha arquitetura transformer avançada para fornecer insights criativos.`,
        `Interessante! Meu treinamento OpenAI me permite abordar isso com versatilidade e precisão, considerando nuances e contexto.`,
        `Ótima pergunta! Como modelo OpenAI, vou aplicar minha capacidade de reasoning para explorar este tópico de forma abrangente.`
      ]
    };
    
    const modelResponses = responses[model];
    const randomIndex = Math.floor(Math.random() * modelResponses.length);
    return modelResponses[randomIndex];
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const currentChat = activeChat;
    
    // Se não há chat ativo, criar um novo
    if (!currentChat) {
      const newChat = {
        id: Date.now().toString(),
        title: message.slice(0, 50) + (message.length > 50 ? '...' : ''),
        messages: [],
        createdAt: new Date()
      };
      
      const userMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: message.trim(),
        sender: 'user',
        timestamp: new Date(),
        model: models[selectedModel].name
      };

      const chatWithMessage = {
        ...newChat,
        messages: [userMessage]
      };

      onUpdateChat(chatWithMessage);
      setIsLoading(true);

      // Simular resposta da IA
      setTimeout(() => {
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          text: getMockResponse(message, selectedModel),
          sender: 'ai',
          timestamp: new Date(),
          model: models[selectedModel].name
        };

        const finalChat = {
          ...chatWithMessage,
          messages: [...chatWithMessage.messages, aiMessage]
        };

        onUpdateChat(finalChat);
        setIsLoading(false);
      }, 1500 + Math.random() * 1000);

      return;
    }

    // Chat já existe, adicionar mensagem
    const userMessage: Message = {
      id: Date.now().toString(),
      text: message.trim(),
      sender: 'user',
      timestamp: new Date(),
      model: models[selectedModel].name
    };

    const updatedChat = {
      ...currentChat,
      messages: [...currentChat.messages, userMessage]
    };

    onUpdateChat(updatedChat);
    setIsLoading(true);

    // Simular resposta da IA
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getMockResponse(userMessage.text, selectedModel),
        sender: 'ai',
        timestamp: new Date(),
        model: models[selectedModel].name
      };

      const finalChat = {
        ...updatedChat,
        messages: [...updatedChat.messages, aiMessage]
      };

      onUpdateChat(finalChat);
      setIsLoading(false);
    }, 1500 + Math.random() * 1000);
  };

  if (!activeChat || activeChat.messages.length === 0) {
    return (
      <S.Container>
        <WelcomeScreen 
          selectedModel={selectedModel}
          onQuickMessage={handleSendMessage}
        />
        <ChatInput 
          selectedModel={selectedModel}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </S.Container>
    );
  }

  return (
    <S.Container>
      <MessagesList 
        messages={activeChat.messages}
        selectedModel={selectedModel}
        isLoading={isLoading}
      />
      <ChatInput 
        selectedModel={selectedModel}
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
      />
    </S.Container>
  );
};

export default ChatArea;