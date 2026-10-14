import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './components/Dashboard';
import { AIChat } from './components/AIChat';
import { MyChart } from './components/MyChart';
import { Auth } from './components/Auth';
import { Muhurta } from './components/Muhurta';

import { Admin } from './components/Admin';
import { Billing } from './components/Billing';
import { Settings } from './components/Settings';
import { useLanguage } from './i18n';
import { useTheme } from './theme';

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const { t, language, setLanguage } = useLanguage();
  const { theme, setTheme } = useTheme();

  if (!token) {
    return <Auth onLogin={setToken} />;
  }

  let isAdmin = false;
  try {
    if (token) {
      const payload = JSON.parse(atob(token.split('.')[1]));
      isAdmin = payload.role === 'admin';
    }
  } catch (e) {
    // invalid token
  }

  const renderContent = () => {
    switch (currentView) {
      case 'dashboard': return <Dashboard />;
      case 'chat': return <AIChat />;
      case 'chart': return <MyChart />;
      case 'muhurta': return <Muhurta />;
      case 'billing': return <Billing />;
      case 'admin': return <Admin />;
      case 'settings': return <Settings />;
      default: return <Dashboard />;
    }
  };

  const getTitle = () => {
    switch (currentView) {
      case 'dashboard': return t('title.dashboard');
      case 'chat': return t('title.chat');
      case 'muhurta': return t('nav.muhurta');
      case 'billing': return t('title.billing');
      case 'admin': return t('title.admin');
      case 'settings': return t('nav.settings').toUpperCase();
      default: return t('title.default');
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', background: 'var(--bg-main)' }}>
      <Sidebar currentView={currentView} onViewChange={setCurrentView} isAdmin={isAdmin} />
      
      <main style={{ flex: 1, padding: '1.5rem 2rem', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          paddingBottom: '1rem',
          borderBottom: '1px solid var(--border-card)',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <h1 style={{ fontWeight: 600, letterSpacing: '1px', fontSize: '1.4rem', color: 'var(--text-main)', margin: 0 }}>
              {getTitle()}
            </h1>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: '2px 0 0 0' }}>
              LUMIRA Astrological Computation Engine
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{t('header.timezone')}</span>
            <div className="badge-tag" style={{ background: 'var(--bg-card-secondary)', border: '1px solid var(--border-card)', color: 'var(--text-main)', padding: '4px 10px' }}>
              {t('header.moon')}
            </div>
            <button 
              onClick={() => setTheme(theme === 'premium' ? 'standard' : 'premium')}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                border: '1px solid var(--border-card)',
                background: theme === 'premium' ? 'rgba(221, 186, 72, 0.15)' : 'var(--bg-card-secondary)',
                color: theme === 'premium' ? 'var(--accent-gold)' : 'var(--text-main)',
                fontSize: '0.8rem',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px'
              }}
              title="Переключить тему (STANDARD / PREMIUM)"
            >
              <span>{theme === 'premium' ? '★ PREMIUM' : 'STANDARD'}</span>
            </button>
            <button 
              onClick={() => setLanguage(language === 'en' ? 'ru' : 'en')}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                border: '1px solid var(--border-card)',
                background: 'var(--bg-card-secondary)',
                color: 'var(--accent-gold)',
                fontSize: '0.8rem',
                fontWeight: 600
              }}
            >
              {language === 'en' ? 'RU' : 'EN'}
            </button>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                setToken(null);
              }}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                border: '1px solid rgba(240, 100, 112, 0.3)',
                background: 'rgba(240, 100, 112, 0.1)',
                color: 'var(--status-error)',
                fontSize: '0.8rem',
                fontWeight: 500
              }}
            >
              {t('settings.logout')}
            </button>
          </div>
        </header>

        <div style={{ flex: 1, paddingBottom: '2rem' }}>
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
