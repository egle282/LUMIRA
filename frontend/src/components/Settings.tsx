import { getApiBaseUrl } from "../api";
import { useState, useEffect } from 'react';
import { useLanguage } from '../i18n';
import { useTheme } from '../theme';
import { Calendar, Clock, MapPin, Globe, Sparkles, Search, Check } from 'lucide-react';

const MONTHS_RU = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

interface CityInfo {
  name: string;
  country?: string;
  lat: number;
  lon: number;
  timezone: string;
}

const CITIES_DATABASE: CityInfo[] = [
  // Россия - Миллионники и крупные центры
  { name: 'Москва', country: 'Россия', lat: 55.7558, lon: 37.6173, timezone: 'Europe/Moscow' },
  { name: 'Санкт-Петербург', country: 'Россия', lat: 59.9343, lon: 30.3351, timezone: 'Europe/Moscow' },
  { name: 'Новосибирск', country: 'Россия', lat: 55.0084, lon: 82.9357, timezone: 'Asia/Novosibirsk' },
  { name: 'Екатеринбург', country: 'Россия', lat: 56.8389, lon: 60.6057, timezone: 'Asia/Yekaterinburg' },
  { name: 'Казань', country: 'Россия', lat: 55.8304, lon: 49.0661, timezone: 'Europe/Moscow' },
  { name: 'Нижний Новгород', country: 'Россия', lat: 56.3269, lon: 44.0059, timezone: 'Europe/Moscow' },
  { name: 'Челябинск', country: 'Россия', lat: 55.1644, lon: 61.4368, timezone: 'Asia/Yekaterinburg' },
  { name: 'Красноярск', country: 'Россия', lat: 56.0153, lon: 92.8932, timezone: 'Asia/Krasnoyarsk' },
  { name: 'Самара', country: 'Россия', lat: 53.1959, lon: 50.1002, timezone: 'Europe/Samara' },
  { name: 'Уфа', country: 'Россия', lat: 54.7388, lon: 55.9721, timezone: 'Asia/Yekaterinburg' },
  { name: 'Ростов-на-Дону', country: 'Россия', lat: 47.2357, lon: 39.7015, timezone: 'Europe/Moscow' },
  { name: 'Омск', country: 'Россия', lat: 54.9885, lon: 73.3242, timezone: 'Asia/Omsk' },
  { name: 'Краснодар', country: 'Россия', lat: 45.0355, lon: 38.9753, timezone: 'Europe/Moscow' },
  { name: 'Воронеж', country: 'Россия', lat: 51.6720, lon: 39.1843, timezone: 'Europe/Moscow' },
  { name: 'Пермь', country: 'Россия', lat: 58.0105, lon: 56.2502, timezone: 'Asia/Yekaterinburg' },
  { name: 'Волгоград', country: 'Россия', lat: 48.7080, lon: 44.5133, timezone: 'Europe/Volgograd' },
  { name: 'Саратов', country: 'Россия', lat: 51.5406, lon: 46.0086, timezone: 'Europe/Saratov' },
  { name: 'Тюмень', country: 'Россия', lat: 57.1530, lon: 65.5343, timezone: 'Asia/Yekaterinburg' },
  { name: 'Тольятти', country: 'Россия', lat: 53.5078, lon: 49.4204, timezone: 'Europe/Samara' },
  { name: 'Барнаул', country: 'Россия', lat: 53.3548, lon: 83.7698, timezone: 'Asia/Barnaul' },
  { name: 'Ижевск', country: 'Россия', lat: 56.8528, lon: 53.2115, timezone: 'Europe/Samara' },
  { name: 'Иркутск', country: 'Россия', lat: 52.2870, lon: 104.3050, timezone: 'Asia/Irkutsk' },
  { name: 'Хабаровск', country: 'Россия', lat: 48.4802, lon: 135.0719, timezone: 'Asia/Vladivostok' },
  { name: 'Ярославль', country: 'Россия', lat: 57.6261, lon: 39.8845, timezone: 'Europe/Moscow' },
  { name: 'Владивосток', country: 'Россия', lat: 43.1198, lon: 131.8869, timezone: 'Asia/Vladivostok' },
  { name: 'Махачкала', country: 'Россия', lat: 42.9831, lon: 47.5047, timezone: 'Europe/Moscow' },
  { name: 'Томск', country: 'Россия', lat: 56.4977, lon: 84.9744, timezone: 'Asia/Tomsk' },
  { name: 'Оренбург', country: 'Россия', lat: 51.7727, lon: 55.0988, timezone: 'Asia/Yekaterinburg' },
  { name: 'Кемерово', country: 'Россия', lat: 55.3547, lon: 86.0872, timezone: 'Asia/Krasnoyarsk' },
  { name: 'Новокузнецк', country: 'Россия', lat: 53.7596, lon: 87.1216, timezone: 'Asia/Krasnoyarsk' },
  { name: 'Рязань', country: 'Россия', lat: 54.6269, lon: 39.6916, timezone: 'Europe/Moscow' },
  { name: 'Астрахань', country: 'Россия', lat: 46.3497, lon: 48.0408, timezone: 'Europe/Astrakhan' },
  { name: 'Пенза', country: 'Россия', lat: 53.2273, lon: 45.0000, timezone: 'Europe/Moscow' },
  { name: 'Липецк', country: 'Россия', lat: 52.6103, lon: 39.5947, timezone: 'Europe/Moscow' },
  { name: 'Тула', country: 'Россия', lat: 54.1961, lon: 37.6182, timezone: 'Europe/Moscow' },
  { name: 'Киров', country: 'Россия', lat: 58.6035, lon: 49.6679, timezone: 'Europe/Kirov' },
  { name: 'Чебоксары', country: 'Россия', lat: 56.1439, lon: 47.2489, timezone: 'Europe/Moscow' },
  { name: 'Калининград', country: 'Россия', lat: 54.7104, lon: 20.4522, timezone: 'Europe/Kaliningrad' },
  { name: 'Сочи', country: 'Россия', lat: 43.6028, lon: 39.7342, timezone: 'Europe/Moscow' },
  { name: 'Улан-Удэ', country: 'Россия', lat: 51.8348, lon: 107.5845, timezone: 'Asia/Irkutsk' },
  { name: 'Ставрополь', country: 'Россия', lat: 45.0428, lon: 41.9734, timezone: 'Europe/Moscow' },
  { name: 'Сургут', country: 'Россия', lat: 61.2540, lon: 73.3962, timezone: 'Asia/Yekaterinburg' },
  { name: 'Тверь', country: 'Россия', lat: 56.8587, lon: 35.9176, timezone: 'Europe/Moscow' },
  { name: 'Иваново', country: 'Россия', lat: 57.0003, lon: 40.9739, timezone: 'Europe/Moscow' },
  { name: 'Брянск', country: 'Россия', lat: 53.2424, lon: 34.3635, timezone: 'Europe/Moscow' },
  { name: 'Белгород', country: 'Россия', lat: 50.5954, lon: 36.5873, timezone: 'Europe/Moscow' },
  { name: 'Архангельск', country: 'Россия', lat: 64.5401, lon: 40.5433, timezone: 'Europe/Moscow' },
  { name: 'Владимир', country: 'Россия', lat: 56.1290, lon: 40.4066, timezone: 'Europe/Moscow' },
  { name: 'Севастополь', country: 'Крым', lat: 44.6166, lon: 33.5254, timezone: 'Europe/Simferopol' },
  { name: 'Симферополь', country: 'Крым', lat: 44.9521, lon: 34.1024, timezone: 'Europe/Simferopol' },
  { name: 'Якутск', country: 'Россия', lat: 62.0355, lon: 129.6755, timezone: 'Asia/Yakutsk' },
  { name: 'Мурманск', country: 'Россия', lat: 68.9585, lon: 33.0827, timezone: 'Europe/Moscow' },
  { name: 'Петропавловск-Камчатский', country: 'Россия', lat: 53.0452, lon: 158.6509, timezone: 'Asia/Kamchatka' },
  { name: 'Южно-Сахалинск', country: 'Россия', lat: 46.9541, lon: 142.7360, timezone: 'Asia/Sakhalin' },

  // СНГ и ближнее зарубежье
  { name: 'Минск', country: 'Беларусь', lat: 53.9006, lon: 27.5590, timezone: 'Europe/Minsk' },
  { name: 'Брест', country: 'Беларусь', lat: 52.0976, lon: 23.7341, timezone: 'Europe/Minsk' },
  { name: 'Гомель', country: 'Беларусь', lat: 52.4345, lon: 30.9754, timezone: 'Europe/Minsk' },
  { name: 'Гродно', country: 'Беларусь', lat: 53.6884, lon: 23.8258, timezone: 'Europe/Minsk' },
  { name: 'Алматы', country: 'Казахстан', lat: 43.2220, lon: 76.8512, timezone: 'Asia/Almaty' },
  { name: 'Астана', country: 'Казахстан', lat: 51.1694, lon: 71.4491, timezone: 'Asia/Almaty' },
  { name: 'Шымкент', country: 'Казахстан', lat: 42.3417, lon: 69.5901, timezone: 'Asia/Almaty' },
  { name: 'Караганда', country: 'Казахстан', lat: 49.8019, lon: 73.1021, timezone: 'Asia/Almaty' },
  { name: 'Ташкент', country: 'Узбекистан', lat: 41.2995, lon: 69.2401, timezone: 'Asia/Tashkent' },
  { name: 'Самарканд', country: 'Узбекистан', lat: 39.6542, lon: 66.9597, timezone: 'Asia/Tashkent' },
  { name: 'Бишкек', country: 'Кыргызстан', lat: 42.8746, lon: 74.5698, timezone: 'Asia/Bishkek' },
  { name: 'Ереван', country: 'Армения', lat: 40.1792, lon: 44.4991, timezone: 'Asia/Yerevan' },
  { name: 'Баку', country: 'Азербайджан', lat: 40.4093, lon: 49.8671, timezone: 'Asia/Baku' },
  { name: 'Тбилиси', country: 'Грузия', lat: 41.7151, lon: 44.8271, timezone: 'Asia/Tbilisi' },
  { name: 'Батуми', country: 'Грузия', lat: 41.6168, lon: 41.6367, timezone: 'Asia/Tbilisi' },
  { name: 'Кишинёв', country: 'Молдова', lat: 47.0105, lon: 28.8638, timezone: 'Europe/Chisinau' },
  { name: 'Киев', country: 'Украина', lat: 50.4501, lon: 30.5234, timezone: 'Europe/Kyiv' },
  { name: 'Одесса', country: 'Украина', lat: 46.4825, lon: 30.7233, timezone: 'Europe/Kyiv' },
  { name: 'Харьков', country: 'Украина', lat: 49.9935, lon: 36.2304, timezone: 'Europe/Kyiv' },

  // Мировые популярные города
  { name: 'Дубай', country: 'ОАЭ', lat: 25.2048, lon: 55.2708, timezone: 'Asia/Dubai' },
  { name: 'Стамбул', country: 'Турция', lat: 41.0082, lon: 28.9784, timezone: 'Europe/Istanbul' },
  { name: 'Анталья', country: 'Турция', lat: 36.8969, lon: 30.7133, timezone: 'Europe/Istanbul' },
  { name: 'Лондон', country: 'Великобритания', lat: 51.5074, lon: -0.1278, timezone: 'Europe/London' },
  { name: 'Париж', country: 'Франция', lat: 48.8566, lon: 2.3522, timezone: 'Europe/Paris' },
  { name: 'Берлин', country: 'Германия', lat: 52.5200, lon: 13.4050, timezone: 'Europe/Berlin' },
  { name: 'Нью-Йорк', country: 'США', lat: 40.7128, lon: -74.0060, timezone: 'America/New_York' },
  { name: 'Лос-Анджелес', country: 'США', lat: 34.0522, lon: -118.2437, timezone: 'America/Los_Angeles' },
  { name: 'Бангкок', country: 'Таиланд', lat: 13.7563, lon: 100.5018, timezone: 'Asia/Bangkok' },
  { name: 'Пхукет', country: 'Таиланд', lat: 7.8804, lon: 98.3923, timezone: 'Asia/Bangkok' },
  { name: 'Бали (Денпасар)', country: 'Индонезия', lat: -8.6705, lon: 115.2126, timezone: 'Asia/Makassar' },
  { name: 'Тель-Авив', country: 'Израиль', lat: 32.0853, lon: 34.7818, timezone: 'Asia/Jerusalem' },
  { name: 'Лимасол', country: 'Кипр', lat: 34.7071, lon: 33.0226, timezone: 'Asia/Nicosia' }
];

const POPULAR_PRESETS = [
  'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Самара', 'Краснодар', 'Сочи', 'Алматы', 'Минск', 'Дубай'
];

export function Settings() {
  const { t, language, setLanguage } = useLanguage();
  const { theme, setTheme } = useTheme();

  // Basic Profile fields
  const [name, setName] = useState('');
  
  // Date sub-parts
  const currentYear = new Date().getFullYear();
  const [birthDay, setBirthDay] = useState(1);
  const [birthMonth, setBirthMonth] = useState(1);
  const [birthYear, setBirthYear] = useState(1990);

  // Time sub-parts
  const [birthHour, setBirthHour] = useState(12);
  const [birthMinute, setBirthMinute] = useState(0);

  // Geolocation
  const [cityQuery, setCityQuery] = useState('');
  const [isCityDropdownOpen, setIsCityDropdownOpen] = useState(false);
  const [lat, setLat] = useState<number | ''>(55.7558);
  const [lon, setLon] = useState<number | ''>(37.6173);
  const [timezone, setTimezone] = useState('Europe/Moscow');

  const [status, setStatus] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${getApiBaseUrl()}/api/profile/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          if (data) {
            setName(data.name || '');
            if (data.birth_date) {
              const dtPart = data.birth_date.split('T')[0];
              const parts = dtPart.split('-');
              if (parts.length === 3) {
                const y = parseInt(parts[0], 10);
                const m = parseInt(parts[1], 10);
                const d = parseInt(parts[2], 10);
                if (!isNaN(y) && y > 1900) setBirthYear(y);
                if (!isNaN(m)) setBirthMonth(m);
                if (!isNaN(d)) setBirthDay(d);
              }
            }
            if (data.birth_time_str) {
              const tParts = data.birth_time_str.split(':');
              if (tParts.length >= 2) {
                const h = parseInt(tParts[0], 10);
                const min = parseInt(tParts[1], 10);
                if (!isNaN(h)) setBirthHour(h);
                if (!isNaN(min)) setBirthMinute(min);
              }
            }
            if (data.lat !== undefined && data.lat !== null) setLat(data.lat);
            if (data.lon !== undefined && data.lon !== null) setLon(data.lon);
            if (data.timezone) setTimezone(data.timezone);
            
            // Try finding matching city name for initial display
            if (data.lat !== undefined && data.lon !== undefined) {
              const matched = CITIES_DATABASE.find(c => 
                Math.abs(c.lat - data.lat) < 0.05 && Math.abs(c.lon - data.lon) < 0.05
              );
              if (matched) {
                setCityQuery(matched.name);
              }
            }
          }
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchProfile();
  }, []);

  const handleSelectCity = (city: CityInfo) => {
    setCityQuery(city.name);
    setLat(city.lat);
    setLon(city.lon);
    setTimezone(city.timezone);
    setIsCityDropdownOpen(false);
  };

  const filteredCities = cityQuery.trim()
    ? CITIES_DATABASE.filter(c =>
        c.name.toLowerCase().includes(cityQuery.trim().toLowerCase()) ||
        (c.country && c.country.toLowerCase().includes(cityQuery.trim().toLowerCase()))
      )
    : [];

  const daysInMonth = (month: number, year: number) => {
    return new Date(year, month, 0).getDate();
  };

  const handleSaveProfile = async () => {
    const maxDays = daysInMonth(birthMonth, birthYear);
    const validDay = Math.min(Math.max(1, birthDay), maxDays);
    const validMonth = Math.min(Math.max(1, birthMonth), 12);
    const validYear = Math.max(1900, Math.min(birthYear, currentYear));

    const formattedDate = `${validYear}-${String(validMonth).padStart(2, '0')}-${String(validDay).padStart(2, '0')}`;
    const formattedTime = `${String(Math.min(23, Math.max(0, birthHour))).padStart(2, '0')}:${String(Math.min(59, Math.max(0, birthMinute))).padStart(2, '0')}`;

    if (!name.trim()) {
      setStatus('Пожалуйста, укажите имя.');
      return;
    }

    if (lat === '' || lon === '' || !timezone.trim()) {
      setStatus('Укажите координаты и часовой пояс рождения.');
      return;
    }

    setIsSaving(true);
    setStatus('Сохранение астрономического профиля…');

    try {
      const token = localStorage.getItem('token');
      const payload = {
        name: name.trim(),
        birth_date: formattedDate,
        birth_time_str: formattedTime,
        lat: Number(lat),
        lon: Number(lon),
        timezone: timezone.trim()
      };

      const res = await fetch(`${getApiBaseUrl()}/api/profile/me`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setStatus('✓ Профиль успешно сохранён. Карты и транзиты пересчитаны!');
        setTimeout(() => setStatus(''), 4000);
      } else if (res.status === 401) {
        setStatus('Сессия истекла или недействительна. Пожалуйста, выполните повторный вход.');
        setTimeout(() => {
          localStorage.removeItem('token');
          window.location.reload();
        }, 1500);
      } else {
        const data = await res.json().catch(() => ({}));
        setStatus(data.detail || 'Ошибка при сохранении профиля.');
      }
    } catch {
      setStatus('Ошибка сети. Проверьте соединение.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  // Generate Year options (descending from currentYear to 1920)
  const yearsList = [];
  for (let y = currentYear; y >= 1920; y--) {
    yearsList.push(y);
  }

  // Days list for currently selected month/year
  const maxDayCount = daysInMonth(birthMonth, birthYear);
  const daysList = Array.from({ length: maxDayCount }, (_, i) => i + 1);

  return (
    <div style={{ maxWidth: '780px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      {/* Settings Header */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, letterSpacing: '1px' }}>
            {t('nav.settings')}
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '2px' }}>
            Управление параметрами вычислений, оформлением и локализацией
          </p>
        </div>
        <div className="badge-tag">
          LUMIRA 1.0
        </div>
      </div>

      {/* Main Settings Card */}
      <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>

        {/* 1. Theme / Appearance Switcher */}
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={18} style={{ color: 'var(--accent-gold)' }} />
            {t('settings.appearance')}
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            {t('settings.theme_desc')}
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <button
              onClick={() => setTheme('standard')}
              style={{
                padding: '1.1rem',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                border: theme === 'standard' ? '2px solid var(--accent-gold)' : '1px solid var(--border-card)',
                background: theme === 'standard' ? 'rgba(221, 186, 72, 0.12)' : 'var(--bg-card-secondary)',
                color: theme === 'standard' ? 'var(--accent-gold)' : 'var(--text-main)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '4px' }}>
                {theme === 'standard' && '✓ '}STANDARD
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Классический cosmic интерфейс
              </div>
            </button>

            <button
              onClick={() => setTheme('premium')}
              style={{
                padding: '1.1rem',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                border: theme === 'premium' ? '2px solid var(--accent-gold)' : '1px solid var(--border-card)',
                background: theme === 'premium' ? 'rgba(221, 186, 72, 0.12)' : 'var(--bg-card-secondary)',
                color: theme === 'premium' ? 'var(--accent-gold)' : 'var(--text-main)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '4px' }}>
                {theme === 'premium' && '★ '}PREMIUM
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Astrology Studio (Dark Luxury)
              </div>
            </button>
          </div>
        </div>

        {/* 2. Language Switcher */}
        <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '1.75rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>{t('settings.language')}</h3>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => setLanguage('en')}
              className="btn-primary"
              style={{
                background: language === 'en' ? 'var(--accent-gold)' : 'transparent',
                color: language === 'en' ? '#080A12' : 'var(--accent-gold)',
                border: '1px solid var(--accent-gold)',
                padding: '8px 18px'
              }}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('ru')}
              className="btn-primary"
              style={{
                background: language === 'ru' ? 'var(--accent-gold)' : 'transparent',
                color: language === 'ru' ? '#080A12' : 'var(--accent-gold)',
                border: '1px solid var(--accent-gold)',
                padding: '8px 18px'
              }}
            >
              Русский
            </button>
          </div>
        </div>

        {/* 3. Astronomical Profile with Refined Date & Time Pickers */}
        <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '1.75rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.4rem', color: 'var(--text-main)' }}>
            {t('settings.profile_title')}
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
            Точные дата, время и географические координаты необходимы для расчёта Лагны (Асцендента), домов и положений планет через Swiss Ephemeris.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Name Input */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                {t('settings.name')}
              </label>
              <input 
                type="text" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                placeholder="Например, Александр" 
                className="studio-input"
              />
            </div>

            {/* Smart Date Selector: Day, Month, Year */}
            <div style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              borderRadius: '10px',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', color: 'var(--accent-gold)' }}>
                <Calendar size={18} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Дата рождения</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1.5fr', gap: '0.75rem' }}>
                {/* Day */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    День
                  </label>
                  <select
                    value={birthDay}
                    onChange={e => setBirthDay(parseInt(e.target.value, 10))}
                    className="studio-input"
                    style={{ cursor: 'pointer' }}
                  >
                    {daysList.map(d => (
                      <option key={d} value={d} style={{ background: '#141521', color: '#FFF' }}>
                        {d}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Month */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Месяц
                  </label>
                  <select
                    value={birthMonth}
                    onChange={e => setBirthMonth(parseInt(e.target.value, 10))}
                    className="studio-input"
                    style={{ cursor: 'pointer' }}
                  >
                    {MONTHS_RU.map((m, idx) => (
                      <option key={idx + 1} value={idx + 1} style={{ background: '#141521', color: '#FFF' }}>
                        {m} ({String(idx + 1).padStart(2, '0')})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Year - Direct number entry + fast dropdown */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Год (1920–{currentYear})
                  </label>
                  <select
                    value={birthYear}
                    onChange={e => setBirthYear(parseInt(e.target.value, 10))}
                    className="studio-input"
                    style={{ cursor: 'pointer', fontFamily: 'monospace' }}
                  >
                    {yearsList.map(y => (
                      <option key={y} value={y} style={{ background: '#141521', color: '#FFF' }}>
                        {y}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Smart Time Selector: Hours & Minutes */}
            <div style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              borderRadius: '10px',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem', color: 'var(--accent-gold)' }}>
                <Clock size={18} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Точное время рождения</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Часы (0–23)
                  </label>
                  <select
                    value={birthHour}
                    onChange={e => setBirthHour(parseInt(e.target.value, 10))}
                    className="studio-input"
                    style={{ cursor: 'pointer', fontFamily: 'monospace' }}
                  >
                    {Array.from({ length: 24 }, (_, i) => (
                      <option key={i} value={i} style={{ background: '#141521', color: '#FFF' }}>
                        {String(i).padStart(2, '0')} ч
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Минуты (0–59)
                  </label>
                  <select
                    value={birthMinute}
                    onChange={e => setBirthMinute(parseInt(e.target.value, 10))}
                    className="studio-input"
                    style={{ cursor: 'pointer', fontFamily: 'monospace' }}
                  >
                    {Array.from({ length: 60 }, (_, i) => (
                      <option key={i} value={i} style={{ background: '#141521', color: '#FFF' }}>
                        {String(i).padStart(2, '0')} мин
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Location & Timezone */}
            <div style={{
              background: 'var(--bg-card-secondary)',
              border: '1px solid var(--border-card)',
              borderRadius: '10px',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem', color: 'var(--accent-gold)' }}>
                <MapPin size={18} />
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Место рождения и координаты</span>
              </div>

              {/* Manual City Input & Autocomplete */}
              <div style={{ marginBottom: '1.25rem', position: 'relative' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Город рождения (введите название или выберите из списка)
                </label>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <Search size={16} style={{ position: 'absolute', left: '12px', color: 'var(--text-muted)', pointerEvents: 'none' }} />
                  <input
                    type="text"
                    value={cityQuery}
                    onChange={e => {
                      setCityQuery(e.target.value);
                      setIsCityDropdownOpen(true);
                    }}
                    onFocus={() => setIsCityDropdownOpen(true)}
                    placeholder="Например: Самара, Тбилиси, Владивосток, Лондон..."
                    className="studio-input"
                    style={{ paddingLeft: '36px', width: '100%' }}
                  />
                  {cityQuery && (
                    <button
                      type="button"
                      onClick={() => {
                        setCityQuery('');
                        setIsCityDropdownOpen(false);
                      }}
                      style={{
                        position: 'absolute',
                        right: '10px',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      ✕
                    </button>
                  )}
                </div>

                {/* Autocomplete Dropdown List */}
                {isCityDropdownOpen && filteredCities.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: 'calc(100% + 4px)',
                    left: 0,
                    right: 0,
                    background: '#161722',
                    border: '1px solid var(--accent-gold-border, rgba(221, 186, 72, 0.3))',
                    borderRadius: '8px',
                    maxHeight: '220px',
                    overflowY: 'auto',
                    zIndex: 100,
                    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)'
                  }}>
                    {filteredCities.slice(0, 10).map((city) => (
                      <div
                        key={`${city.name}-${city.country || ''}`}
                        onClick={() => handleSelectCity(city)}
                        style={{
                          padding: '10px 14px',
                          cursor: 'pointer',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                          transition: 'background 0.15s ease'
                        }}
                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(221, 186, 72, 0.1)')}
                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                      >
                        <div>
                          <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                            {city.name}
                          </span>
                          {city.country && (
                            <span style={{ marginLeft: '8px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              ({city.country})
                            </span>
                          )}
                        </div>
                        <div style={{ textAlign: 'right', fontSize: '0.75rem', color: 'var(--accent-gold)' }}>
                          {city.timezone.split('/')[1] || city.timezone}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick City Presets */}
              <div style={{ marginBottom: '1rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
                  Быстрый выбор популярного города:
                </span>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {CITIES_DATABASE.filter(c => POPULAR_PRESETS.includes(c.name)).map(c => {
                    const isSelected = timezone === c.timezone && 
                      lat !== '' && Math.abs(Number(lat) - c.lat) < 0.05 && 
                      lon !== '' && Math.abs(Number(lon) - c.lon) < 0.05;
                    return (
                      <button
                        key={c.name}
                        type="button"
                        onClick={() => handleSelectCity(c)}
                        style={{
                          padding: '4px 10px',
                          borderRadius: '6px',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          border: '1px solid var(--border-card)',
                          background: isSelected ? 'rgba(221, 186, 72, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                          color: isSelected ? 'var(--accent-gold)' : 'var(--text-secondary)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}
                      >
                        {isSelected && <Check size={12} />}
                        {c.name}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Широта (Lat)
                  </label>
                  <input 
                    type="number" 
                    step="0.0001"
                    placeholder="55.7558"
                    value={lat} 
                    onChange={e => setLat(e.target.value === '' ? '' : Number(e.target.value))} 
                    className="studio-input"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Долгота (Lon)
                  </label>
                  <input 
                    type="number" 
                    step="0.0001"
                    placeholder="37.6173"
                    value={lon} 
                    onChange={e => setLon(e.target.value === '' ? '' : Number(e.target.value))} 
                    className="studio-input"
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                  Часовой пояс (IANA Timezone)
                </label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Globe size={16} style={{ color: 'var(--text-muted)' }} />
                  <input 
                    type="text" 
                    value={timezone} 
                    onChange={e => setTimezone(e.target.value)} 
                    placeholder="Europe/Moscow" 
                    className="studio-input"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button & Status */}
            <div>
              <button
                type="button"
                onClick={handleSaveProfile}
                disabled={isSaving}
                className="btn-primary"
                style={{ width: '100%', padding: '12px', fontSize: '1rem' }}
              >
                {isSaving ? 'Сохранение…' : t('settings.save_btn')}
              </button>

              {status && (
                <div style={{
                  marginTop: '1rem',
                  padding: '0.75rem 1rem',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  textAlign: 'center',
                  background: status.startsWith('✓') ? 'rgba(67, 201, 128, 0.15)' : 'rgba(241, 106, 118, 0.15)',
                  border: status.startsWith('✓') ? '1px solid var(--status-success)' : '1px solid var(--status-error)',
                  color: status.startsWith('✓') ? 'var(--status-success)' : 'var(--status-error)'
                }}>
                  {status}
                </div>
              )}
            </div>

          </div>
        </div>

        {/* 4. Logout Section */}
        <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>Завершение сеанса</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Выход из текущей учётной записи на этом устройстве</div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              padding: '8px 18px',
              background: 'transparent',
              border: '1px solid var(--status-error)',
              color: 'var(--status-error)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '0.85rem'
            }}
          >
            {t('settings.logout')}
          </button>
        </div>

      </div>
    </div>
  );
}
