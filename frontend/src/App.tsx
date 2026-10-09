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

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const { t, language, setLanguage } = useLanguage();

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
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar currentView={currentView} onViewChange={setCurrentView} isAdmin={isAdmin} />
      
      <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <h1 style={{ fontWeight: 300, letterSpacing: '2px', color: 'var(--accent-gold)' }}>
            {getTitle()}
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              onClick={() => setLanguage(language === 'en' ? 'ru' : 'en')}
              className="glass-panel"
              style={{ padding: '0.5rem 1rem', borderRadius: '20px', cursor: 'pointer', border: 'none', background: 'rgba(212, 175, 55, 0.1)', color: 'var(--accent-gold)' }}
            >
              {language === 'en' ? 'RU' : 'EN'}
            </button>
            <span style={{ color: 'var(--text-muted)' }}>Mumbai, India (Local Time)</span>
            <div className="glass-panel" style={{ padding: '0.5rem 1rem', borderRadius: '20px' }}>
              Moon in Taurus ☽
            </div>
          </div>
        </header>

        {renderContent()}
      </main>
    </div>
  );
}
