import styled from 'styled-components';

export const Container = styled.aside<{ $isOpen: boolean }>`
  width: 320px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(34, 197, 94, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.1);
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    width: 280px;
    transform: translateX(${props => props.$isOpen ? '0' : '-100%'});
    border-right: 1px solid rgba(34, 197, 94, 0.2);
    box-shadow: ${props => props.$isOpen ? '4px 0 20px rgba(0, 0, 0, 0.15)' : 'none'};
  }
  
  @media (min-width: 769px) {
    transform: translateX(${props => props.$isOpen ? '0' : '-320px'});
    margin-left: ${props => props.$isOpen ? '0' : '-320px'};
  }
`;

export const Header = styled.div`
  padding: 24px 20px;
  border-bottom: 1px solid rgba(34, 197, 94, 0.1);
  
  @media (max-width: 768px) {
    padding: 20px 16px;
  }
`;

export const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: #16a34a;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
    margin-bottom: 16px;
  }
`;

export const NewChatButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
  }
  
  @media (max-width: 768px) {
    padding: 10px 14px;
    font-size: 0.9rem;
  }
`;

export const ChatList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(34, 197, 94, 0.1);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(34, 197, 94, 0.3);
    border-radius: 3px;
  }
  
  @media (max-width: 768px) {
    padding: 12px;
  }
`;

export const ChatItem = styled.div<{ $isActive: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.$isActive ? 'rgba(34, 197, 94, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.$isActive ? 'rgba(34, 197, 94, 0.2)' : 'transparent'};
  position: relative;
  
  &:hover {
    background: rgba(34, 197, 94, 0.05);
    transform: translateX(4px);
    
    button {
      opacity: 1;
    }
  }
  
  @media (max-width: 768px) {
    padding: 12px;
    gap: 8px;
    
    &:hover {
      transform: none;
    }
  }
`;

export const ChatInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

export const ChatTitle = styled.div`
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #1e293b;
  
  @media (max-width: 768px) {
    font-size: 0.85rem;
  }
`;

export const ChatPreview = styled.div`
  font-size: 0.8rem;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  
  @media (max-width: 768px) {
    font-size: 0.75rem;
  }
`;

export const DeleteButton = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.3s ease;
  opacity: 0;
  
  &:hover {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
  }
  
  @media (max-width: 768px) {
    opacity: 1;
  }
`;