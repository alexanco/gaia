import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 50%, #a7f3d0 100%);
  color: #1e293b;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  position: relative;
  overflow: hidden;
`;

export const Overlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;
  
  @media (max-width: 768px) {
    display: block;
  }
`;

export const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(240, 253, 244, 0.8);
  position: relative;
  width: 100%;
  min-width: 0;
`;