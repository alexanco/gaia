import React from 'react';
import { Bot, Sparkles, Brain, Zap, MoreVertical, X } from 'lucide-react';
import { Chat, AIModel } from '../../pages/Home/Home';
import * as S from './styles';

interface HeaderProps {
  activeChat: Chat | undefined;
  selectedModel: AIModel;
  sidebarOpen: boolean;
  onModelChange: (model: AIModel) => void;
  onToggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({
  activeChat,
  selectedModel,
  sidebarOpen,
  onModelChange,
  onToggleSidebar
}) => {
  const models = {
    claude: { name: 'Claude', icon: Bot, color: '#16a34a', company: 'Anthropic' },
    deepseek: { name: 'DeepSeek', icon: Brain, color: '#15803d', company: 'DeepSeek' },
    gemini: { name: 'Gemini', icon: Sparkles, color: '#166534', company: 'Google' },
    openai: { name: 'GPT-4', icon: Zap, color: '#22c55e', company: 'OpenAI' }
  };

  return (
    <S.Container>
      <S.LeftSection>
        <S.MenuButton onClick={onToggleSidebar}>
          {sidebarOpen ? <X size={20} /> : <MoreVertical size={20} />}
        </S.MenuButton>
        <S.Title>
          {activeChat?.title || 'Gaia AI Chat'}
        </S.Title>
      </S.LeftSection>
      
      <S.ModelSelector>
        {(Object.keys(models) as AIModel[]).map(modelKey => {
          const model = models[modelKey];
          const IconComponent = model.icon;
          return (
            <S.ModelButton
              key={modelKey}
              $isActive={selectedModel === modelKey}
              $color={model.color}
              onClick={() => onModelChange(modelKey)}
              title={`${model.name} - ${model.company}`}
            >
              <IconComponent size={18} />
              <span>{model.name}</span>
            </S.ModelButton>
          );
        })}
      </S.ModelSelector>
    </S.Container>
  );
};

export default Header;