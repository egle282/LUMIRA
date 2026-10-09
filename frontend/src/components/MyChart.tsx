import { useEffect, useState } from 'react';
import { Compass } from 'lucide-react';
import { useLanguage } from '../i18n';

interface PlanetData {
  sign: string;
  degree: number;
  nakshatra_index: number;
  pada: number;
  is_retrograde: boolean;
}

interface ChartData {
  ayanamsa: number;
  planets: Record<string, PlanetData>;
}

const planetTranslations: Record<string, { en: string, ru: string }> = {
  Sun: { en: 'Sun', ru: 'Солнце' },
  Moon: { en: 'Moon', ru: 'Луна' },
  Mars: { en: 'Mars', ru: 'Марс' },
  Mercury: { en: 'Mercury', ru: 'Меркурий' },
  Jupiter: { en: 'Jupiter', ru: 'Юпитер' },
  Venus: { en: 'Venus', ru: 'Венера' },
  Saturn: { en: 'Saturn', ru: 'Сатурн' },
  Rahu: { en: 'Rahu', ru: 'Раху' },
  Ketu: { en: 'Ketu', ru: 'Кету' }
};

export function MyChart() {
  const [data, setData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    const fetchChart = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('http://localhost:8000/api/chart/natal', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!res.ok) throw new Error('Failed to fetch chart data');
        const result = await res.json();
        if (result.error) throw new Error(result.error);
        setData(result);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchChart();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
        <p className="text-gradient" style={{ fontSize: '1.2rem', animation: 'pulseGlow 2s infinite' }}>
          {language === 'ru' ? 'Рассчитываем математику вашей Судьбы...' : 'Calculating the math of your Destiny...'}
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: '#ff6b6b' }}>
        <p>{language === 'ru' ? 'Ошибка:' : 'Error:'} {error}</p>
        <p style={{ fontSize: '0.9rem', marginTop: '1rem', color: 'var(--text-muted)' }}>
          {language === 'ru' ? '(Возможно, не указана дата рождения в профиле)' : '(Perhaps birth date is not set in profile)'}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h2 className="text-gradient" style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
          <Compass size={28} />
          {language === 'ru' ? 'Астрономические Координаты (Раси)' : 'Astronomical Coordinates (Rasi)'}
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
          {language === 'ru' 
            ? 'Здесь представлены точные позиции планет в вашей натальной карте, рассчитанные с помощью Swiss Ephemeris.' 
            : 'Here are the exact planetary positions in your natal chart, calculated via Swiss Ephemeris.'}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
          {data && Object.entries(data.planets).map(([planet, info]) => (
            <div key={planet} className="glass-panel glow-hover" style={{ padding: '1.5rem', background: 'rgba(20, 20, 30, 0.4)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.2rem', color: 'var(--accent-gold)' }}>
                  {planetTranslations[planet]?.[language] || planet}
                  {info.is_retrograde && <span style={{ fontSize: '0.8rem', color: '#ff6b6b', marginLeft: '0.5rem' }}>(R)</span>}
                </h3>
                <span style={{ fontSize: '1.2rem', fontWeight: 300 }}>{info.degree.toFixed(2)}°</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', color: 'var(--text-main)', fontSize: '0.95rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{language === 'ru' ? 'Знак:' : 'Sign:'}</span>
                  <span>{info.sign}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{language === 'ru' ? 'Накшатра:' : 'Nakshatra:'}</span>
                  <span>#{info.nakshatra_index} (Пада {info.pada})</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div style={{ marginTop: '2rem', textAlign: 'right', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Ayanamsa: {data?.ayanamsa.toFixed(4)}° (Lahiri)
        </div>
      </div>
    </div>
  );
}
