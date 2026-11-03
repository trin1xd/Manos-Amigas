import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import AdultoMayorDashboard from './pages/AdultoMayor/AdultoMayorDashboard';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AdultoMayorDashboard />
  </React.StrictMode>
);
