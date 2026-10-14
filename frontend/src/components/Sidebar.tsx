import { useState } from 'react';
import { LayoutDashboard, MessageSquare, Compass, Calendar, Settings, CreditCard, Shield, Info, Sparkles } from 'lucide-react';
import { useLanguage } from '../i18n';
import { InfoModal } from './InfoModal';

export function Sidebar({ currentView, onViewChange, isAdmin }: { currentView: string, onViewChange: (view: string) => void, isAdmin: boolean }) {
  const [showInfo, setShowInfo] = useState(false);
  const { t } = useLanguage();
  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: t('nav.dashboard') },
    { id: 'chart', icon: Compass, label: t('nav.chart') },
    { id: 'chat', icon: MessageSquare, label: t('nav.chat') },
    { id: 'muhurta', icon: Calendar, label: t('nav.muhurta') },
    { id: 'billing', icon: CreditCard, label: t('nav.billing') },
  ];
  if (isAdmin) {
    navItems.push({ id: 'admin', icon: Shield, label: t('nav.admin') });
  }

  return (
    <aside style={{
      width: '240px',
      minWidth: '240px',
      background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-card)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem 0.85rem',
      height: '100vh',
      boxSizing: 'border-box'
    }}>
      {/* Brand Header */}
      <div style={{ padding: '0 0.5rem 1.75rem 0.5rem', borderBottom: '1px solid var(--border-card)', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Sparkles size={18} style={{ color: 'var(--accent-gold)' }} />
          <h2 style={{ letterSpacing: '3px', fontWeight: 700, fontSize: '1.25rem', color: 'var(--text-main)', margin: 0 }}>
            LUMIRA
          </h2>
        </div>
        <p style={{ fontSize: '0.72rem', color: 'var(--accent-gold)', letterSpacing: '1px', textTransform: 'uppercase', margin: 0, fontWeight: 500 }}>
          Astrology Studio
        </p>
      </div>

      {/* Navigation List */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, overflowY: 'auto' }}>
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 14px',
                background: isActive ? 'rgba(221, 186, 72, 0.12)' : 'transparent',
                border: 'none',
                borderLeft: isActive ? '3px solid var(--accent-gold)' : '3px solid transparent',
                borderRadius: '0 8px 8px 0',
                color: isActive ? 'var(--accent-gold)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                textAlign: 'left',
                fontSize: '0.9rem',
                width: '100%'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                  e.currentTarget.style.color = 'var(--text-main)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <item.icon size={18} style={{ color: isActive ? 'var(--accent-gold)' : 'inherit', flexShrink: 0 }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Bottom Controls */}
      <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '1rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <button 
          onClick={() => setShowInfo(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 14px',
            background: 'transparent',
            border: 'none',
            borderRadius: '6px',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            textAlign: 'left',
            fontSize: '0.85rem'
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text-main)'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.background = 'transparent'; }}
        >
          <Info size={16} /> {t('nav.info')}
        </button>

        <button 
          onClick={() => onViewChange('settings')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '8px 14px',
            background: currentView === 'settings' ? 'rgba(221, 186, 72, 0.12)' : 'transparent',
            border: 'none',
            borderLeft: currentView === 'settings' ? '3px solid var(--accent-gold)' : '3px solid transparent',
            borderRadius: '0 6px 6px 0',
            color: currentView === 'settings' ? 'var(--accent-gold)' : 'var(--text-secondary)',
            cursor: 'pointer',
            textAlign: 'left',
            fontSize: '0.85rem'
          }}
          onMouseEnter={(e) => {
            if (currentView !== 'settings') {
              e.currentTarget.style.color = 'var(--text-main)';
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
            }
          }}
          onMouseLeave={(e) => {
            if (currentView !== 'settings') {
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.background = 'transparent';
            }
          }}
        >
          <Settings size={16} /> {t('nav.settings')}
        </button>
      </div>

      {showInfo && <InfoModal onClose={() => setShowInfo(false)} />}
    </aside>
  );
}
