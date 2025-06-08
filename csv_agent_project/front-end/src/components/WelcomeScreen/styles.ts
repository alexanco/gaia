import styled from 'styled-components';

export const Container = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  
  @media (max-width: 768px) {
    padding: 20px;
  }
`;

export const Content = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 600px;
  width: 100%;
`;

export const ModelIcon = styled.div<{ $color: string }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  background: ${props => props.$color + '10'};
  border: 2px solid ${props => props.$color + '30'};
  border-radius: 24px;
  color: ${props => props.$color};
  margin-bottom: 24px;
  
  @media (max-width: 768px) {
    width: 80px;
    height: 80px;
    margin-bottom: 16px;
    
    svg {
      width: 40px;
      height: 40px;
    }
  }
`;

export const Title = styled.h2`
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  
  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`;

export const Subtitle = styled.p`
  margin: 0 0 32px 0;
  color: #64748b;
  font-size: 1.1rem;
  
  @media (max-width: 768px) {
    font-size: 1rem;
    margin-bottom: 24px;
  }
`;

export const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  width: 100%;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    max-width: 300px;
    gap: 8px;
  }
`;

export const QuickButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  background: rgba(34, 197, 94, 0.05);
  border: 1px solid rgba(34, 197, 94, 0.1);
  border-radius: 12px;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  font-weight: 500;
  
  .emoji {
    font-size: 1.2rem;
  }
  
  &:hover {
    background: rgba(34, 197, 94, 0.1);
    transform: translateY(-2px);
    border-color: rgba(34, 197, 94, 0.2);
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 0.85rem;
  }
`;