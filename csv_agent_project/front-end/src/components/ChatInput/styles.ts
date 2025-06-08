import styled from 'styled-components';

export const Container = styled.div`
  padding: 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(34, 197, 94, 0.1);
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

export const InputWrapper = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 16px;
  padding: 16px;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.05);
  
  &:focus-within {
    border-color: rgba(34, 197, 94, 0.4);
    background: rgba(255, 255, 255, 1);
  }
  
  @media (max-width: 768px) {
    padding: 12px;
    gap: 8px;
  }
`;

export const TextArea = styled.textarea`
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #1e293b;
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
  min-height: 24px;
  max-height: 120px;
  font-family: inherit;
  
  &::placeholder {
    color: #64748b;
  }
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.3);
    border-radius: 2px;
  }
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
`;

export const SendButton = styled.button<{ $hasContent: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: ${props => props.$hasContent 
    ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
    : 'rgba(34, 197, 94, 0.1)'
  };
  color: ${props => props.$hasContent ? 'white' : '#64748b'};
  cursor: ${props => props.$hasContent ? 'pointer' : 'not-allowed'};
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
  }
  
  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
`;

export const Hint = styled.div`
  margin-top: 8px;
  font-size: 0.8rem;
  color: #64748b;
  text-align: center;
  
  @media (max-width: 768px) {
    font-size: 0.75rem;
    display: none;
  }
`;