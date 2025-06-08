// src/routes/Routes.tsx - Com Lazy Loading, Refinarias e Usuários
import { Routes, Route, Navigate } from "react-router-dom";
import Home from "../pages/Home/Home";

const AppRoutes = () => {
  return (
    <Routes>
      
      <Route path="/" element={<Home />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;