import styled from 'styled-components';

export const Container = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(34, 197, 94, 0.1);
  box-shadow: 0 2px 10px rgba(34, 197, 94, 0.05);
  
  @media (max-width: 768px) {
    padding: 16px 20px;
    flex-wrap: wrap;
    gap: 12px;
  }
`;

export const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  
  @media (max-width: 768px) {
    gap: 12px;
    flex: 1;
  }
`;

export const Title = styled.h1`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  
  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

export const MenuButton = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
  }
`;

export const ModelSelector = styled.div`
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  padding: 6px;
  border-radius: 12px;
  border: 1px solid rgba(34, 197, 94, 0.1);
  box-shadow: 0 2px 10px rgba(34, 197, 94, 0.05);
  
  @media (max-width: 768px) {
    width: 100%;
    order: 3;
    justify-content: space-between;
    padding: 4px;
    gap: 4px;
  }
`;

export const ModelButton = styled.button<{ $isActive: boolean; $color: string }>`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background: ${props => props.$isActive ? props.$color + '15' : 'transparent'};
  color: ${props => props.$isActive ? props.$color : '#64748b'};
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  font-weight: 500;
  
  &:hover {
    background: ${props => props.$color + '10'};
    color: ${props => props.$color};
  }
  
  @media (max-width: 768px) {
    padding: 6px 8px;
    font-size: 0.8rem;
    
    span {
      display: none;
    }
  }
  
  @media (max-width: 480px) {
    padding: 6px;
  }
`;