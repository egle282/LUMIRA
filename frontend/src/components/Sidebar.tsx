import { useState } from 'react';
import { LayoutDashboard, MessageSquare, Compass, Calendar, Settings, CreditCard, Shield, Info } from 'lucide-react';
import { useLanguage } from '../i18n';
import { InfoModal } from './InfoModal';

export function Sidebar({ currentView, onViewChange, isAdmin }: { currentView: string, onViewChange: (view: string) => void, isAdmin: boolean }) {
  const [showInfo, setShowInfo] = useState(false);
  const { t } = useLanguage();
  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: t('nav.dashboard') },
    { id: 'chat', icon: MessageSquare, label: t('nav.chat') },
    { id: 'chart', icon: Compass, label: t('nav.chart') },
    { id: 'muhurta', icon: Calendar, label: t('nav.muhurta') },
    { id: 'billing', icon: CreditCard, label: t('nav.billing') },
  ];
  if (isAdmin) {
    navItems.push({ id: 'admin', icon: Shield, label: t('nav.admin') });
  }

  return (
    <aside className="glass-panel" style={{ width: '260px', margin: '1rem', padding: '2rem 1rem', display: 'flex', flexDirection: 'column' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h2 style={{ letterSpacing: '4px', fontWeight: 600 }}>LUMIRA</h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--accent-gold)' }}>AI VEDIC ASTROLOGER</p>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem',
                background: isActive ? 'rgba(212, 175, 55, 0.1)' : 'transparent',
                border: isActive ? '1px solid rgba(212, 175, 55, 0.3)' : '1px solid transparent',
                borderRadius: '12px', color: isActive ? 'var(--accent-gold)' : 'var(--text-muted)',
                cursor: 'pointer', transition: 'all 0.3s ease', textAlign: 'left', fontSize: '1rem'
              }}
              className="glow-hover"
            >
              <item.icon size={20} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <button 
          onClick={() => setShowInfo(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem',
            background: 'transparent', border: 'none', color: 'var(--text-muted)',
            cursor: 'pointer', textAlign: 'left', fontSize: '1rem'
          }}
          className="glow-hover"
        >
          <Info size={20} /> {t('nav.info')}
        </button>

        <button 
          onClick={() => onViewChange('settings')}
          style={{
            display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem',
            background: 'transparent', border: 'none', color: 'var(--text-muted)',
            cursor: 'pointer', textAlign: 'left', fontSize: '1rem'
          }}
          className="glow-hover"
        >
          <Settings size={20} /> {t('nav.settings')}
        </button>
      </div>

      {showInfo && <InfoModal onClose={() => setShowInfo(false)} />}
    </aside>
  );
}
