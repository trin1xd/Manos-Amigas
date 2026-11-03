import { useState } from 'react';
import './index.css';

import Hero from './components/home/Hero';
import ComoFunciona from './components/home/ComoFunciona';
import Seguridad from './components/home/Seguridad';
import Servicios from './components/home/Servicios';
import Footer from './components/layout/Footer';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import RegistrationForm from './pages/Register/RegistrationForm';

function App() {
  const [currentView, setCurrentView] = useState('inicio');

  if (currentView === 'login') {
    return <Login onNavigateHome={() => setCurrentView('inicio')} />;
  }

  if (currentView === 'crear-cuenta') {
    return <Register onNavigateHome={() => setCurrentView('inicio')} onSelectRole={(role) => setCurrentView(`registro:${role}`)} />;
  }

  if (currentView.startsWith('registro:')) {
    return (
      <RegistrationForm
        key={currentView}
        role={currentView.split(':')[1]}
        onBack={() => setCurrentView('crear-cuenta')}
        onLogin={() => setCurrentView('login')}
      />
    );
  }

  return (
    <>
      <main id="main-content">
        <Hero
          onLoginClick={() => setCurrentView('login')}
          onCreateAccountClick={() => setCurrentView('crear-cuenta')}
        />
        <ComoFunciona />
        <Seguridad />
        <Servicios />
      </main>
      <Footer />
    </>
  );
}

export default App;
