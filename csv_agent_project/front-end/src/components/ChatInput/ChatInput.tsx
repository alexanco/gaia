import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { AIModel } from '../../pages/Home/Home';
import * as S from './styles';

interface ChatInputProps {
  selectedModel: AIModel;
  isLoading: boolean;
  onSendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  selectedModel,
  isLoading,
  onSendMessage
}) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const models = {
    claude: 'Claude',
    deepseek: 'DeepSeek',
    gemini: 'Gemini',
    openai: 'GPT-4'
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputValue]);

  const handleSend = () => {
    if (!inputValue.trim() || isLoading) return;
    
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <S.Container>
      <S.InputWrapper>
        <S.TextArea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={`Conversar com ${models[selectedModel]}...`}
          disabled={isLoading}
          rows={1}
        />
        <S.SendButton
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading}
          $hasContent={!!inputValue.trim()}
        >
          <Send size={20} />
        </S.SendButton>
      </S.InputWrapper>
      <S.Hint>
        Pressione Enter para enviar • Shift+Enter para quebra de linha
      </S.Hint>
    </S.Container>
  );
};

export default ChatInput;