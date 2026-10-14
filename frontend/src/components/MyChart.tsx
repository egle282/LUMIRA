import { useEffect, useState } from 'react';
import { getApiBaseUrl } from '../api';
import { Compass, User, Globe, Calendar, Clock, Sparkles } from 'lucide-react';
import { useLanguage } from '../i18n';
import { NatalWheel, PlanetPosition, HouseCusp, AspectData } from './NatalWheel';

const PLANET_METADATA: Record<string, { ru: string; glyph: string; color: string }> = {
  Sun: { ru: 'Солнце', glyph: '☉', color: '#F0A94B' },
  Moon: { ru: 'Луна', glyph: '☽', color: '#E8EAED' },
  Mars: { ru: 'Марс', glyph: '♂', color: '#F06470' },
  Mercury: { ru: 'Меркурий', glyph: '☿', color: '#5DB88C' },
  Jupiter: { ru: 'Юпитер', glyph: '♃', color: '#DDBA48' },
  Venus: { ru: 'Венера', glyph: '♀', color: '#E8A5C8' },
  Saturn: { ru: 'Сатурн', glyph: '♄', color: '#8A99AD' },
  Rahu: { ru: 'Раху', glyph: '☊', color: '#A06CD5' },
  Ketu: { ru: 'Кету', glyph: '☋', color: '#6C757D' },
};

const NAKSHATRAS = [
  'Ашвини', 'Бхарани', 'Криттика', 'Рохини', 'Мригашира', 'Ардра',
  'Пунарвасу', 'Пушья', 'Ашлеша', 'Магха', 'Пурва Пхалгуни', 'Уттара Пхалгуни',
  'Хаста', 'Читра', 'Свати', 'Вишакха', 'Анурадха', 'Джйештха',
  'Мула', 'Пурва Ашадха', 'Уттара Ашадха', 'Шравана', 'Дхаништха', 'Шатабхиша',
  'Пурва Бхадрапада', 'Уттара Бхадрапада', 'Ревати'
];

interface RawChartResponse {
  ayanamsa: number;
  planets: Record<string, {
    sign: string;
    sign_index?: number;
    degree: number;
    abs_degree?: number;
    nakshatra_index: number;
    pada: number;
    is_retrograde: boolean;
  }>;
  ascendant?: {
    longitude: number;
    sign: string;
    degree: number;
  };
  mc?: {
    longitude: number;
    sign: string;
    degree: number;
  };
  houses?: HouseCusp[];
  aspects?: AspectData[];
  profile?: {
    name: string;
    birth_date: string;
    birth_time: string;
    lat: number;
    lon: number;
    timezone: string;
  };
}

export function MyChart() {
  const [data, setData] = useState<RawChartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'planets' | 'houses' | 'aspects'>('planets');
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);
  const { t } = useLanguage();

  useEffect(() => {
    const fetchChart = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${getApiBaseUrl()}/api/chart/natal`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.detail || 'Не удалось загрузить данные карты');
        }
        const result: RawChartResponse = await res.json();
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
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '3px solid rgba(221, 186, 72, 0.2)',
            borderTopColor: 'var(--accent-gold)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1.5rem auto'
          }} />
          <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
          <p className="text-gradient" style={{ fontSize: '1.1rem', fontWeight: 500 }}>
            {t('chart.loading')}
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel" style={{ padding: '3rem 2rem', textAlign: 'center', maxWidth: '600px', margin: '2rem auto' }}>
        <Compass size={44} style={{ color: 'var(--status-error)', marginBottom: '1rem' }} />
        <h3 style={{ color: 'var(--status-error)', marginBottom: '0.5rem' }}>{t('chart.error')}</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>{error}</p>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          {t('chart.no_profile')}
        </p>
      </div>
    );
  }

  // Transform planets for the NatalWheel
  const planetsList: PlanetPosition[] = Object.entries(data.planets).map(([key, info]) => {
    const meta = PLANET_METADATA[key] || { ru: key, glyph: '●', color: 'var(--accent-gold)' };
    const absDeg = info.abs_degree ?? ((info.sign_index ?? 0) * 30 + info.degree);
    return {
      name: key,
      name_ru: meta.ru,
      sign: info.sign,
      sign_index: info.sign_index ?? Math.floor(absDeg / 30) % 12,
      degree: info.degree,
      abs_degree: absDeg,
      nakshatra_index: info.nakshatra_index,
      pada: info.pada,
      is_retrograde: info.is_retrograde,
      glyph: meta.glyph,
      color: meta.color,
    };
  });

  const asc = data.ascendant || { longitude: 0, sign: 'Овен', degree: 0 };
  const mc = data.mc;
  const houses = data.houses || [];
  const aspects = data.aspects || [];
  const profile = data.profile;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%' }}>
      {/* Studio Header Bar */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'rgba(221, 186, 72, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(221, 186, 72, 0.25)'
          }}>
            <Compass size={24} style={{ color: 'var(--accent-gold)' }} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 600 }}>{profile?.name || 'Натальная Карта'}</h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Сидерический Зодиак (Lahiri) • Дома Плацидуса • Swiss Ephemeris
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div className="badge-tag">
            Аянамша: {data.ayanamsa.toFixed(4)}°
          </div>
          <div className="badge-tag" style={{ background: 'rgba(91, 141, 239, 0.1)', borderColor: 'rgba(91, 141, 239, 0.3)', color: '#7AA7F5' }}>
            9 Граха (Grahams)
          </div>
        </div>
      </div>

      {/* 3-Column Studio Grid Layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '280px 1fr 380px',
        gap: '1.5rem',
        alignItems: 'start',
      }}>
        {/* LEFT COLUMN: Subject / Birth Parameters */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <h3 style={{ fontSize: '0.95rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={16} style={{ color: 'var(--accent-gold)' }} />
            Данные субъекта
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', fontSize: '0.85rem' }}>
            <div style={{ borderBottom: '1px solid var(--border-card)', paddingBottom: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>ФИО / Имя</div>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '2px' }}>{profile?.name || '—'}</div>
            </div>

            <div style={{ borderBottom: '1px solid var(--border-card)', paddingBottom: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Calendar size={13} /> Дата рождения
              </div>
              <div style={{ fontWeight: 500, color: 'var(--text-main)', marginTop: '2px' }}>{profile?.birth_date || '—'}</div>
            </div>

            <div style={{ borderBottom: '1px solid var(--border-card)', paddingBottom: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Clock size={13} /> Время рождения
              </div>
              <div style={{ fontWeight: 500, color: 'var(--text-main)', marginTop: '2px' }}>{profile?.birth_time || '12:00'}</div>
            </div>

            <div style={{ borderBottom: '1px solid var(--border-card)', paddingBottom: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Globe size={13} /> Координаты (Шир/Долг)
              </div>
              <div style={{ fontWeight: 500, color: 'var(--text-main)', marginTop: '2px' }}>
                {profile?.lat !== undefined ? `${profile.lat.toFixed(2)}°, ${profile.lon.toFixed(2)}°` : '—'}
              </div>
            </div>

            <div style={{ borderBottom: '1px solid var(--border-card)', paddingBottom: '8px' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Часовой пояс</div>
              <div style={{ fontWeight: 500, color: 'var(--text-main)', marginTop: '2px' }}>{profile?.timezone || '—'}</div>
            </div>
          </div>

          <div style={{ marginTop: '0.5rem', background: 'var(--bg-card-secondary)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-card)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--accent-gold)', fontWeight: 600, marginBottom: '6px' }}>
              Кардинальные точки
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Асцендент (Лагна):</span>
              <span style={{ fontWeight: 600 }}>{asc.degree.toFixed(2)}° {asc.sign.split(' ')[0]}</span>
            </div>
            {mc && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>MC (Середина Неба):</span>
                <span style={{ fontWeight: 600 }}>{mc.degree.toFixed(2)}° {mc.sign.split(' ')[0]}</span>
              </div>
            )}
          </div>
        </div>

        {/* CENTER COLUMN: Vector Natal Wheel */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} style={{ color: 'var(--accent-gold)' }} />
              Круговая Векторная Карта
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Векторная модель (SVG)</span>
          </div>

          <NatalWheel
            planets={planetsList}
            houses={houses}
            ascendant={asc}
            mc={mc}
            aspects={aspects}
            selectedPlanet={selectedPlanet}
            onSelectPlanet={(p) => setSelectedPlanet(p.name === selectedPlanet ? null : p.name)}
          />
        </div>

        {/* RIGHT COLUMN: Studio Data Tables & Tabs */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          {/* Tab Navigation */}
          <div className="studio-tabs">
            <button
              className={`studio-tab-btn ${activeTab === 'planets' ? 'active' : ''}`}
              onClick={() => setActiveTab('planets')}
            >
              Планеты ({planetsList.length})
            </button>
            <button
              className={`studio-tab-btn ${activeTab === 'houses' ? 'active' : ''}`}
              onClick={() => setActiveTab('houses')}
            >
              Дома ({houses.length})
            </button>
            <button
              className={`studio-tab-btn ${activeTab === 'aspects' ? 'active' : ''}`}
              onClick={() => setActiveTab('aspects')}
            >
              Аспекты ({aspects.length})
            </button>
          </div>

          {/* TAB 1: Planets Table */}
          {activeTab === 'planets' && (
            <div style={{ overflowX: 'auto', maxHeight: '560px', overflowY: 'auto' }}>
              <table className="studio-table">
                <thead>
                  <tr>
                    <th>Планета</th>
                    <th>Знак</th>
                    <th>Градус</th>
                    <th>Накшатра</th>
                  </tr>
                </thead>
                <tbody>
                  {planetsList.map((p) => {
                    const isSelected = selectedPlanet === p.name;
                    return (
                      <tr
                        key={p.name}
                        onClick={() => setSelectedPlanet(isSelected ? null : p.name)}
                        style={{
                          cursor: 'pointer',
                          background: isSelected ? 'rgba(221, 186, 72, 0.12)' : undefined,
                        }}
                      >
                        <td style={{ fontWeight: 600 }}>
                          <span style={{ color: p.color, marginRight: '6px', fontSize: '1.1rem' }}>{p.glyph}</span>
                          {p.name_ru}
                          {p.is_retrograde && <span className="badge-retro" style={{ marginLeft: '6px' }}>R</span>}
                        </td>
                        <td>{p.sign.split(' ')[0]}</td>
                        <td style={{ fontFamily: 'monospace' }}>{p.degree.toFixed(2)}°</td>
                        <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                          {NAKSHATRAS[p.nakshatra_index] || `#${p.nakshatra_index + 1}`} (п.{p.pada})
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 2: Houses Table */}
          {activeTab === 'houses' && (
            <div style={{ overflowX: 'auto', maxHeight: '560px', overflowY: 'auto' }}>
              <table className="studio-table">
                <thead>
                  <tr>
                    <th>Дом</th>
                    <th>Куспид</th>
                    <th>Знак</th>
                    <th>Градус</th>
                  </tr>
                </thead>
                <tbody>
                  {houses.map((h) => {
                    const isAngular = [1, 4, 7, 10].includes(h.house);
                    return (
                      <tr key={h.house}>
                        <td style={{ fontWeight: isAngular ? 700 : 500, color: isAngular ? 'var(--accent-gold)' : undefined }}>
                          {h.house} {isAngular && '★'}
                        </td>
                        <td style={{ fontFamily: 'monospace' }}>{h.longitude.toFixed(2)}°</td>
                        <td>{h.sign.split(' ')[0]}</td>
                        <td style={{ fontFamily: 'monospace' }}>{h.degree.toFixed(2)}°</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: Aspects Table */}
          {activeTab === 'aspects' && (
            <div style={{ overflowX: 'auto', maxHeight: '560px', overflowY: 'auto' }}>
              {aspects.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
                  Мажорные аспекты не обнаружены в пределах установленного орбиса.
                </p>
              ) : (
                <table className="studio-table">
                  <thead>
                    <tr>
                      <th>Планеты</th>
                      <th>Аспект</th>
                      <th>Угол</th>
                      <th>Орбис</th>
                    </tr>
                  </thead>
                  <tbody>
                    {aspects.map((asp, idx) => {
                      const p1Meta = PLANET_METADATA[asp.planet1];
                      const p2Meta = PLANET_METADATA[asp.planet2];
                      let natureBadge = null;
                      if (asp.nature === 'harmonious') {
                        natureBadge = <span style={{ color: 'var(--status-success)' }}>{asp.name_ru}</span>;
                      } else if (asp.nature === 'challenging') {
                        natureBadge = <span style={{ color: 'var(--status-error)' }}>{asp.name_ru}</span>;
                      } else {
                        natureBadge = <span style={{ color: 'var(--accent-gold)' }}>{asp.name_ru}</span>;
                      }

                      return (
                        <tr key={`aspect-${idx}`}>
                          <td style={{ fontWeight: 500, whiteSpace: 'nowrap' }}>
                            <span style={{ color: p1Meta?.color }}>{p1Meta?.ru || asp.planet1}</span>
                            {' ↔ '}
                            <span style={{ color: p2Meta?.color }}>{p2Meta?.ru || asp.planet2}</span>
                          </td>
                          <td>
                            <span style={{ marginRight: '6px', fontWeight: 'bold' }}>{asp.symbol}</span>
                            {natureBadge}
                          </td>
                          <td style={{ fontFamily: 'monospace' }}>{asp.angle}°</td>
                          <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{asp.orb.toFixed(2)}°</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
