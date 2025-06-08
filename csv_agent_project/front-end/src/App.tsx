// src/App.tsx - Como integrar os providers
import { BrowserRouter } from 'react-router-dom';

import AppRoutes from './routes/Routes';

function App() {
  return (
    <BrowserRouter>
            <AppRoutes />
    </BrowserRouter>
  );
}

export default App;