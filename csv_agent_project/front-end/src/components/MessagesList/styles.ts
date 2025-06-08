import styled from 'styled-components';

export const Container = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(34, 197, 94, 0.1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.3);
    border-radius: 4px;
  }
  
  @media (max-width: 768px) {
    padding: 16px;
    gap: 16px;
  }
`;

export const MessageContainer = styled.div<{ $isUser: boolean }>`
  display: flex;
  justify-content: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
`;

export const MessageBubble = styled.div<{ $isUser: boolean; $color: string }>`
  position: relative;
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 16px;
  background: ${props => props.$isUser 
    ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
    : 'rgba(255, 255, 255, 0.9)'
  };
  border: 1px solid ${props => props.$isUser 
    ? 'rgba(34, 197, 94, 0.3)'
    : 'rgba(34, 197, 94, 0.1)'
  };
  backdrop-filter: blur(20px);
  color: ${props => props.$isUser ? 'white' : '#1e293b'};
  box-shadow: 0 4px 20px ${props => props.$isUser 
    ? 'rgba(34, 197, 94, 0.2)' 
    : 'rgba(34, 197, 94, 0.05)'
  };
  
  @media (max-width: 768px) {
    max-width: 85%;
    padding: 12px 16px;
  }
`;

export const MessageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

export const MessageSender = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  opacity: 0.8;
`;

export const MessageTime = styled.span`
  font-size: 0.7rem;
  opacity: 0.6;
`;

export const MessageText = styled.p`
  margin: 0;
  line-height: 1.6;
  word-wrap: break-word;
`;

export const CopyButton = styled.button`
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(34, 197, 94, 0.1);
  border: none;
  border-radius: 6px;
  padding: 6px;
  color: #64748b;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
  
  ${MessageBubble}:hover & {
    opacity: 1;
  }
  
  &:hover {
    background: rgba(34, 197, 94, 0.2);
    color: #16a34a;
  }
`;

export const LoadingBubble = styled.div<{ $color: string }>`
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(34, 197, 94, 0.1);
  backdrop-filter: blur(20px);
  font-style: italic;
  color: #64748b;
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.05);
  
  @media (max-width: 768px) {
    max-width: 85%;
    padding: 12px 16px;
  }
`;

export const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  
  div {
    width: 6px;
    height: 6px;
    background: #64748b;
    border-radius: 50%;
    animation: bounce 1.4s ease-in-out infinite both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;