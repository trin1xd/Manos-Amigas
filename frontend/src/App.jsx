
import { useEffect, useState } from 'react';
import './index.css';

import Hero from './components/home/Hero';
import ComoFunciona from './components/home/ComoFunciona';
import Seguridad from './components/home/Seguridad';
import Servicios from './components/home/Servicios';
import Footer from './components/layout/Footer';

import Login from './pages/Login/Login';
import Register from './pages/Register/Register';
import RegistrationForm from './pages/Register/RegistrationForm';

import AdultoMayorOperativo from './pages/AdultoMayor/AdultoMayorOperativo';
import UniversitarioDashboard from './pages/Universitario/UniversitarioDashboard';
import FamiliarDashboardOperativo from './pages/Familiar/FamiliarDashboardOperativo';
import AdminVerificaciones from './pages/Admin/AdminVerificaciones';

import {
  getMe,
  hasToken,
  logout,
} from './services/sessionService';

function App() {
  const [currentView, setCurrentView] = useState('inicio');
  const [usuario, setUsuario] = useState(null);
  const [verificandoSesion, setVerificandoSesion] = useState(true);
  const [errorSesion, setErrorSesion] = useState('');

  // Escucha la expiración desde cualquier dashboard (excepto el login público).
  useEffect(() => {
    const sesionExpirada = () => {
      setUsuario(null);
      setCurrentView('login');
      setErrorSesion('Tu sesión expiró. Inicia sesión nuevamente.');
    };
    window.addEventListener('manos-amigas:sesion-expirada', sesionExpirada);
    return () => window.removeEventListener('manos-amigas:sesion-expirada', sesionExpirada);
  }, []);

  // Recuperar sesión al recargar la página
  useEffect(() => {
    let activo = true;

    async function recuperarSesion() {
      if (!hasToken()) {
        if (activo) setVerificandoSesion(false);
        return;
      }

      try {
        const data = await getMe();

        if (activo) {
          setUsuario(data.user);
        }
      } catch {
        logout();

        if (activo) {
          setUsuario(null);
        }
      } finally {
        if (activo) {
          setVerificandoSesion(false);
        }
      }
    }

    recuperarSesion();

    return () => {
      activo = false;
    };
  }, []);

  // Se ejecuta después del login exitoso
  async function handleLoginSuccess() {
    try {
      const data = await getMe();

      if (!data?.user) {
        throw new Error('No se pudo verificar el usuario.');
      }

      setUsuario(data.user);
      setErrorSesion('');
    } catch {
      logout();
      setUsuario(null);
      setErrorSesion(
        'No se pudo verificar la sesión. Intenta iniciar sesión nuevamente.'
      );
    }
  }

  function handleLogout() {
    logout();
    setUsuario(null);
    setCurrentView('inicio');
    setErrorSesion('');
  }

  if (verificandoSesion) {
    return (
      <main className="container" style={{ padding: '3rem' }}>
        <p>Verificando tu sesión...</p>
      </main>
    );
  }

  // Dashboard del adulto mayor autenticado
  if (usuario?.rol === 'ADULTO_MAYOR') {
    return (
      <AdultoMayorOperativo
        usuario={usuario}
        onLogout={handleLogout}
      />
    );
  }

  // Paneles por rol: la sesión fue validada mediante /api/auth/me.
  if (usuario?.rol === 'UNIVERSITARIO') {
    return (
      <UniversitarioDashboard usuario={usuario} onLogout={handleLogout} />
    );
  }

  if (usuario?.rol === 'FAMILIAR') {
    return (
      <FamiliarDashboardOperativo usuario={usuario} onLogout={handleLogout} />
    );
  }

  if (usuario?.rol === 'ADMIN') {
    return <AdminVerificaciones usuario={usuario} onLogout={handleLogout} />;
  }

  if (usuario) {
    return (
      <main className="container" style={{ padding: '3rem' }}>
        <h1>Bienvenido/a, {usuario.nombre}</h1>
        <p>Perfil: {usuario.rol}</p>
        <p>
          Tu sesión está activa. El dashboard de este perfil
          está en desarrollo.
        </p>
        <button type="button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </main>
    );
  }

  if (currentView === 'login') {
    return (
      <>
        <Login
          onNavigateHome={() => setCurrentView('inicio')}
          onNavigateRegister={() => setCurrentView('crear-cuenta')}
          onLoginSuccess={handleLoginSuccess}
        />
        {errorSesion && (
          <p role="alert" style={{ color: '#b91c1c', textAlign: 'center' }}>
            {errorSesion}
          </p>
        )}
      </>
    );
  }

  if (currentView === 'crear-cuenta') {
    return (
      <Register
        onNavigateHome={() => setCurrentView('inicio')}
        onSelectRole={(role) =>
          setCurrentView(`registro:${role}`)
        }
      />
    );
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
          onCreateAccountClick={() =>
            setCurrentView('crear-cuenta')
          }
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
