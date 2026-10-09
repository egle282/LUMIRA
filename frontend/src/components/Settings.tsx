import { useState, useEffect } from 'react';
import { useLanguage } from '../i18n';

export function Settings() {
  const { t, language, setLanguage } = useLanguage();
  
  const [profile, setProfile] = useState({
    name: '',
    birth_date: '1990-01-01',
    birth_time_str: '12:00',
    lat: 19.0760,
    lon: 72.8777,
    timezone: 'Asia/Kolkata'
  });
  const [status, setStatus] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8000/api/profile/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data) {
            setProfile({
              name: data.name,
              birth_date: data.birth_date.split('T')[0],
              birth_time_str: data.birth_time_str,
              lat: data.lat,
              lon: data.lon,
              timezone: data.timezone
            });
          }
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchProfile();
  }, []);

  const handleSaveProfile = async () => {
    setStatus('Сохранение...');
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('http://localhost:8000/api/profile/me', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(profile)
      });
      if (res.ok) {
        setStatus('Профиль сохранен успешно!');
        setTimeout(() => setStatus(''), 3000);
      } else {
        setStatus('Ошибка при сохранении.');
      }
    } catch (err) {
      setStatus('Ошибка сети.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px', maxWidth: '600px' }}>
      <h2 style={{ color: 'var(--accent-gold)', marginBottom: '2rem' }}>{t('nav.settings')}</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <div>
          <h3 style={{ marginBottom: '1rem' }}>{t('settings.language')}</h3>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              onClick={() => setLanguage('en')}
              className={`btn-primary`}
              style={{ background: language === 'en' ? 'var(--accent-gold)' : 'transparent', color: language === 'en' ? '#000' : 'var(--accent-gold)', border: '1px solid var(--accent-gold)' }}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('ru')}
              className={`btn-primary`}
              style={{ background: language === 'ru' ? 'var(--accent-gold)' : 'transparent', color: language === 'ru' ? '#000' : 'var(--accent-gold)', border: '1px solid var(--accent-gold)' }}
            >
              Русский
            </button>
          </div>
        </div>

        <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>{language === 'ru' ? 'Астрономический Профиль' : 'Astronomical Profile'}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input 
              type="text" 
              value={profile.name} 
              onChange={e => setProfile({...profile, name: e.target.value})} 
              placeholder={language === 'ru' ? 'Ваше имя' : 'Your name'} 
              style={{ padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
            />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <input 
                type="date" 
                value={profile.birth_date} 
                onChange={e => setProfile({...profile, birth_date: e.target.value})} 
                style={{ flex: 1, padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
              />
              <input 
                type="time" 
                value={profile.birth_time_str} 
                onChange={e => setProfile({...profile, birth_time_str: e.target.value})} 
                style={{ flex: 1, padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
              />
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <input 
                type="number" 
                placeholder="Latitude (e.g. 55.75)"
                value={profile.lat} 
                onChange={e => setProfile({...profile, lat: parseFloat(e.target.value)})} 
                style={{ flex: 1, padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
              />
              <input 
                type="number" 
                placeholder="Longitude (e.g. 37.61)"
                value={profile.lon} 
                onChange={e => setProfile({...profile, lon: parseFloat(e.target.value)})} 
                style={{ flex: 1, padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
              />
            </div>
            <input 
              type="text" 
              value={profile.timezone} 
              onChange={e => setProfile({...profile, timezone: e.target.value})} 
              placeholder="Timezone (e.g. Europe/Moscow)" 
              style={{ padding: '0.8rem', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px' }} 
            />
            <button
              onClick={handleSaveProfile}
              className="glow-hover"
              style={{ padding: '0.8rem 1.5rem', background: 'var(--accent-gold)', border: 'none', color: 'black', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, marginTop: '0.5rem' }}
            >
              {language === 'ru' ? 'Сохранить профиль' : 'Save Profile'}
            </button>
            {status && <span style={{ color: 'var(--accent-gold)', fontSize: '0.9rem' }}>{status}</span>}
          </div>
        </div>

        <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '2rem' }}>
          <button
            onClick={handleLogout}
            style={{ padding: '0.8rem 1.5rem', background: 'transparent', border: '1px solid #ff6b6b', color: '#ff6b6b', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}
          >
            {t('settings.logout')}
          </button>
        </div>
      </div>
    </div>
  );
}
