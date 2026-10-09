import { useState } from 'react';
import { useLanguage } from '../i18n';

export function Auth({ onLogin }: { onLogin: (token: string) => void }) {
  const { t, language, setLanguage } = useLanguage();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    const url = isRegister ? '/api/auth/register' : '/api/auth/token';
    const body = isRegister 
      ? JSON.stringify({ email, password })
      : new URLSearchParams({ username: email, password });
      
    try {
      const response = await fetch(`http://localhost:8000${url}`, {
        method: 'POST',
        headers: isRegister 
          ? { 'Content-Type': 'application/json' }
          : { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body as any
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');
      
      localStorage.setItem('token', data.access_token);
      onLogin(data.access_token);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'absolute', top: '1rem', right: '1rem' }}>
        <button 
          onClick={() => setLanguage(language === 'en' ? 'ru' : 'en')}
          className="glass-panel"
          style={{ padding: '0.5rem 1rem', borderRadius: '20px', cursor: 'pointer', border: 'none', background: 'rgba(212, 175, 55, 0.1)', color: 'var(--accent-gold)' }}
        >
          {language === 'en' ? 'RU' : 'EN'}
        </button>
      </div>
      <div className="glass-panel" style={{ padding: '3rem', width: '400px', borderRadius: '12px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--accent-gold)' }}>
          {isRegister ? (language === 'en' ? 'JOIN LUMIRA' : 'ПРИСОЕДИНИТЬСЯ') : (language === 'en' ? 'ENTER LUMIRA' : 'ВОЙТИ')}
        </h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input 
            type="email" 
            placeholder={t('auth.email')}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--accent-gold)', color: 'white', borderRadius: '8px' }}
            required
          />
          <input 
            type="password" 
            placeholder={t('auth.password')}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '1rem', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--accent-gold)', color: 'white', borderRadius: '8px' }}
            required
          />
          {error && <div style={{ color: '#ff6b6b', fontSize: '0.9rem' }}>{error}</div>}
          <button type="submit" style={{ padding: '1rem', background: 'var(--accent-gold)', color: '#0d1117', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>
            {isRegister ? t('auth.register') : t('auth.login')}
          </button>
        </form>
        <p style={{ textAlign: 'center', marginTop: '1.5rem', cursor: 'pointer', color: 'var(--text-muted)' }} onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? t('auth.switch_to_login') : t('auth.switch_to_register')}
        </p>
      </div>
    </div>
  );
}
