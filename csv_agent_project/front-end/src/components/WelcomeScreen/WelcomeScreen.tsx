import React from 'react';
import { Bot, Sparkles, Brain, Zap } from 'lucide-react';
import { AIModel } from '../../pages/Home/Home';
import * as S from './styles';

interface WelcomeScreenProps {
  selectedModel: AIModel;
  onQuickMessage: (message: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  selectedModel,
  onQuickMessage
}) => {
  const models = {
    claude: { name: 'Claude', icon: Bot, color: '#16a34a', company: 'Anthropic' },
    deepseek: { name: 'DeepSeek', icon: Brain, color: '#15803d', company: 'DeepSeek' },
    gemini: { name: 'Gemini', icon: Sparkles, color: '#166534', company: 'Google' },
    openai: { name: 'GPT-4', icon: Zap, color: '#22c55e', company: 'OpenAI' }
  };

  const quickMessages = [
    {
      emoji: '🍀',
      title: 'Cumprimentar',
      message: 'Olá! Como você pode me ajudar hoje?'
    },
    {
      emoji: '🌱',
      title: 'Explicar conceito',
      message: 'Explique um conceito complexo de forma simples'
    },
    {
      emoji: '🌿',
      title: 'Ajuda com código',
      message: 'Me ajude a resolver um problema de programação'
    },
    {
      emoji: '🍃',
      title: 'Brainstorming',
      message: 'Vamos fazer um brainstorming criativo?'
    }
  ];

  const modelInfo = models[selectedModel];
  const IconComponent = modelInfo.icon;

  return (
    <S.Container>
      <S.Content>
        <S.ModelIcon $color={modelInfo.color}>
          <IconComponent size={64} />
        </S.ModelIcon>
        
        <S.Title>
          Conversar com {modelInfo.name}
        </S.Title>
        
        <S.Subtitle>
          Desenvolvido pela {modelInfo.company}
        </S.Subtitle>
        
        <S.QuickActions>
          {quickMessages.map((item, index) => (
            <S.QuickButton
              key={index}
              onClick={() => onQuickMessage(item.message)}
            >
              <span className="emoji">{item.emoji}</span>
              {item.title}
            </S.QuickButton>
          ))}
        </S.QuickActions>
      </S.Content>
    </S.Container>
  );
};

export default WelcomeScreen;