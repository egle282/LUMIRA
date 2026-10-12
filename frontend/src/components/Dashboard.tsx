import { getApiBaseUrl } from "../api";
import { useEffect, useState } from 'react';
import { useLanguage } from '../i18n';

export function Dashboard() {
  const { t } = useLanguage();
  const [briefing, setBriefing] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const headers = { 'Authorization': `Bearer ${token}` };
        
        const [briefingRes, profileRes] = await Promise.all([
          fetch(`${getApiBaseUrl()}/api/briefing/daily`, { headers }),
          fetch(`${getApiBaseUrl()}/api/profile/me`, { headers })
        ]);

        if (briefingRes.ok) {
          setBriefing(await briefingRes.json());
        }
        if (profileRes.ok) {
          setProfile(await profileRes.json());
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)' }}>{t('dash.loading')}</div>;
  }

  if (error) {
    return <div style={{ color: '#ff6b6b' }}>{error}</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome Banner */}
      <section className="glass-panel" style={{ padding: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '2rem', color: 'var(--accent-gold)', marginBottom: '0.5rem' }}>
            Намасте, {profile?.name || 'Искатель'} ✨
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
            Звезды готовы открыть вам свои секреты на сегодня.
          </p>
        </div>
        {profile && profile.birth_date && (
          <div style={{ textAlign: 'right', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '0.9rem' }}>Ваши данные:</div>
            <div style={{ color: 'white', fontWeight: 500 }}>{profile.birth_date} • {profile.birth_time}</div>
            <div style={{ color: 'white', fontWeight: 500 }}>{profile.city}</div>
          </div>
        )}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          {/* Daily Briefing Card */}
        <section className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>{t('dash.briefing')}</h3>
          {briefing?.is_mock && (
            <div style={{ padding: '1rem', marginBottom: '1rem', background: 'rgba(255, 107, 107, 0.1)', borderLeft: '4px solid #ff6b6b', borderRadius: '4px' }}>
              <strong style={{ color: '#ff6b6b' }}>Внимание:</strong> ИИ-ассистент временно недоступен. Показан базовый астрологический прогноз.
            </div>
          )}
          <p style={{ fontSize: '1.2rem', lineHeight: '1.6', fontWeight: 300 }}>
            {briefing?.ai_interpretation || t('dash.no_interp')}
          </p>
          
          <div style={{ marginTop: '2rem', display: 'flex', gap: '2rem' }}>
            {briefing?.recommendations?.length > 0 && (
              <div style={{ flex: 1 }}>
                <strong style={{ color: '#4caf50' }}>{t('dash.do')}</strong>
                <ul style={{ marginTop: '0.5rem', color: 'var(--text-muted)', paddingLeft: '1.2rem' }}>
                  {briefing.recommendations.map((r: string, i: number) => <li key={i}>{r}</li>)}
                </ul>
              </div>
            )}
            {briefing?.cautions?.length > 0 && (
              <div style={{ flex: 1 }}>
                <strong style={{ color: '#ff6b6b' }}>{t('dash.dont')}</strong>
                <ul style={{ marginTop: '0.5rem', color: 'var(--text-muted)', paddingLeft: '1.2rem' }}>
                  {briefing.cautions.map((c: string, i: number) => <li key={i}>{c}</li>)}
                </ul>
              </div>
            )}
          </div>
        </section>

        {/* Current Transits */}
        <section className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>{t('dash.transits')}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            {briefing?.key_transits?.map((t_item: any, i: number) => (
              <div key={i} style={{ padding: '1rem', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
                <strong style={{ color: 'var(--accent-gold)' }}>{t_item.planet} {t('dash.in')} {t_item.current_sign} ({t('dash.house')} {t_item.house_transiting})</strong>
                <p style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                  {t('dash.impact')}: {t_item.impact}
                </p>
              </div>
            ))}
          </div>
        </section>

      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Panchanga Card */}
        <section className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{t('dash.panchanga')}</h3>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.tithi')}</span>
              <span>{briefing?.panchanga?.tithi}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.vara')}</span>
              <span>{briefing?.panchanga?.vara}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.nakshatra')}</span>
              <span>{briefing?.panchanga?.nakshatra}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.yoga')}</span>
              <span>{briefing?.panchanga?.yoga}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.karana')}</span>
              <span>{briefing?.panchanga?.karana}</span>
            </li>
            <li style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem', marginTop: '0.5rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>{t('dash.auspiciousness')}</span>
              <span style={{ color: 'var(--accent-gold)', fontWeight: 'bold' }}>{briefing?.panchanga?.auspiciousness_score}/10</span>
            </li>
          </ul>
        </section>
        
        {/* Focus Areas */}
        <section className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{t('dash.areas')}</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {briefing?.focus_life_areas?.map((area: string, i: number) => (
              <span key={i} style={{ padding: '0.3rem 0.8rem', background: 'rgba(212, 175, 55, 0.2)', color: 'var(--accent-gold)', borderRadius: '20px', fontSize: '0.9rem', textTransform: 'capitalize' }}>
                {area}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
    </div>
  );
}
