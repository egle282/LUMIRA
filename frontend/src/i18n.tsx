import { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'en' | 'ru';

interface Translations {
  [key: string]: {
    en: string;
    ru: string;
  };
}

export const translations: Translations = {
  // Sidebar
  'nav.dashboard': { en: 'Dashboard', ru: 'Главная' },
  'nav.chat': { en: 'AI Astrologer', ru: 'ИИ Астролог' },
  'nav.chart': { en: 'My Chart', ru: 'Моя Карта' },
  'nav.muhurta': { en: 'Muhurta', ru: 'Мухурта' },
  'nav.billing': { en: 'Subscription', ru: 'Подписка' },
  'nav.admin': { en: 'Admin Panel', ru: 'Админ Панель' },
  'nav.settings': { en: 'Settings', ru: 'Настройки' },
  'nav.info': { en: 'Information', ru: 'О проекте' },
  
  // App
  'title.dashboard': { en: 'MY JOURNEY', ru: 'МОЙ ПУТЬ' },
  'title.chat': { en: 'ORACLE CHAT', ru: 'ОРАКУЛ ЧАТ' },
  'title.billing': { en: 'SUBSCRIPTION', ru: 'ПОДПИСКА' },
  'title.admin': { en: 'ADMINISTRATOR', ru: 'АДМИНИСТРАТОР' },
  'title.default': { en: 'LUMIRA', ru: 'LUMIRA' },
  
  // Auth
  'auth.login': { en: 'Login', ru: 'Войти' },
  'auth.register': { en: 'Register', ru: 'Регистрация' },
  'auth.email': { en: 'Email', ru: 'Email' },
  'auth.password': { en: 'Password', ru: 'Пароль' },
  'auth.switch_to_register': { en: 'Need an account? Register', ru: 'Нет аккаунта? Зарегистрироваться' },
  'auth.switch_to_login': { en: 'Already have an account? Login', ru: 'Уже есть аккаунт? Войти' },
  
  // Admin
  'admin.title': { en: 'Admin Dashboard', ru: 'Панель Управления' },
  'admin.login_title': { en: 'Admin Access Required', ru: 'Требуется вход администратора' },
  'admin.login_desc': { en: 'You are currently logged in as a standard user. Enter administrator credentials to access management controls.', ru: 'Вы вошли как обычный пользователь. Введите данные администратора для доступа к управлению.' },
  'admin.login_btn': { en: 'Sign in as Admin', ru: 'Войти как Администратор' },
  'admin.tokens': { en: 'AI Chat Messages', ru: 'Сообщения AI-чата' },
  'admin.cost': { en: 'Provider Cost Tracking', ru: 'Учёт расходов провайдера' },
  'admin.cost_unavailable': { en: 'Not tracked yet', ru: 'Пока не отслеживается' },
  'admin.users': { en: 'User Management', ru: 'Управление пользователями' },
  'admin.email': { en: 'Email', ru: 'Email' },
  'admin.role': { en: 'Role', ru: 'Роль' },
  'admin.joined': { en: 'Joined', ru: 'Дата регистрации' },
  
  // Billing
  'billing.title': { en: 'Subscription & Billing', ru: 'Подписка и Биллинг' },
  'billing.current': { en: 'Current Plan:', ru: 'Текущий тариф:' },
  'billing.status': { en: 'Status:', ru: 'Статус:' },
  'billing.free': { en: 'Free', ru: 'Бесплатный' },
  'billing.upgrade_pro': { en: 'Upgrade to Pro', ru: 'Перейти на Pro' },
  'billing.upgrade_premium': { en: 'Upgrade to Premium', ru: 'Перейти на Premium' },
  'billing.current_plan_btn': { en: 'Current Plan', ru: 'Текущий тариф' },
  'billing.pro_desc': { en: 'All current features with 50 AI chat messages per day.', ru: 'Все текущие функции и до 50 сообщений AI-чату в день.' },
  'billing.premium_desc': { en: 'All current features with an expanded daily AI chat limit.', ru: 'Все текущие функции и увеличенный дневной лимит AI-чата.' },

  // Dashboard
  'dash.briefing': { en: 'DAILY BRIEFING', ru: 'ДНЕВНОЙ БРИФИНГ' },
  'dash.transits': { en: 'KEY TRANSITS', ru: 'КЛЮЧЕВЫЕ ТРАНЗИТЫ' },
  'dash.panchanga': { en: "TODAY'S PANCHANGA", ru: 'ПАНЧАНГА НА СЕГОДНЯ' },
  'dash.areas': { en: 'ACTIVE LIFE AREAS', ru: 'АКТИВНЫЕ СФЕРЫ ЖИЗНИ' },
  'dash.loading': { en: 'Consulting the stars...', ru: 'Спрашиваем звезды...' },
  'dash.no_interp': { en: 'No interpretation available today.', ru: 'Интерпретация на сегодня недоступна.' },
  'dash.impact': { en: 'Impact', ru: 'Влияние' },
  'dash.auspiciousness': { en: 'Auspiciousness', ru: 'Благоприятность' },
  'dash.house': { en: 'House', ru: 'Дом' },
  'dash.in': { en: 'in', ru: 'в' },
  'dash.do': { en: 'DO', ru: 'ЧТО ДЕЛАТЬ' },
  'dash.dont': { en: "DON'T", ru: 'ЧЕГО ИЗБЕГАТЬ' },
  'dash.tithi': { en: 'Tithi', ru: 'Титхи' },
  'dash.vara': { en: 'Vara (Day)', ru: 'Вара (День)' },
  'dash.nakshatra': { en: 'Nakshatra', ru: 'Накшатра' },
  'dash.yoga': { en: 'Yoga', ru: 'Йога' },
  'dash.karana': { en: 'Karana', ru: 'Карана' },

  // App header
  'header.timezone': { en: 'Mumbai, India (Local Time)', ru: 'Москва, Россия (Местное время)' },
  'header.moon': { en: 'Moon in Taurus ☽', ru: 'Луна в Тельце ☽' },

  // Settings
  'settings.appearance': { en: 'Appearance & Theme', ru: 'Внешний вид и Тема' },
  'settings.theme_standard': { en: 'STANDARD (Classic)', ru: 'STANDARD (Классическая)' },
  'settings.theme_premium': { en: 'PREMIUM (Astrology Studio)', ru: 'PREMIUM (Астрологическая Студия)' },
  'settings.theme_desc': { en: 'Switch between the classic interface and the dark luxury astrology studio.', ru: 'Переключение между классическим оформлением и тёмной профессиональной студией.' },
  'settings.language': { en: 'Language', ru: 'Язык' },
  'settings.logout': { en: 'Logout', ru: 'Выйти из аккаунта' },
  'settings.profile_title': { en: 'Astronomical Profile', ru: 'Астрономический Профиль' },
  'settings.name': { en: 'Your Name', ru: 'Ваше имя' },
  'settings.lat': { en: 'Latitude (e.g. 55.75)', ru: 'Широта (например, 55.75)' },
  'settings.lon': { en: 'Longitude (e.g. 37.61)', ru: 'Долгота (например, 37.61)' },
  'settings.timezone': { en: 'Timezone (e.g. Europe/Moscow)', ru: 'Часовой пояс (например, Europe/Moscow)' },
  'settings.save_btn': { en: 'Save Profile', ru: 'Сохранить профиль' },
  'settings.saving': { en: 'Saving…', ru: 'Сохранение…' },
  'settings.saved': { en: 'Profile saved successfully.', ru: 'Профиль сохранён успешно.' },
  'settings.err_fill': { en: 'Complete all fields. Latitude must be −90 to 90 and longitude −180 to 180.', ru: 'Заполните все поля. Широта должна быть от −90 до 90, долгота — от −180 до 180.' },

  // Muhurta
  'muhurta.title': { en: 'Muhurta · Panchanga', ru: 'Мухурта · Панчанга' },
  'muhurta.desc': { en: 'Preliminary hourly screening of lunar day and nakshatra by saved location and timezone.', ru: 'Предварительный почасовой скрининг лунного дня и накшатры по сохранённому месту и часовому поясу.' },
  'muhurta.event_date': { en: 'Event Date', ru: 'Дата события' },
  'muhurta.event_type': { en: 'Event Type', ru: 'Тип события' },
  'muhurta.calc_btn': { en: 'Calculate Panchanga', ru: 'Рассчитать Панчангу' },
  'muhurta.calculating': { en: 'Calculating…', ru: 'Рассчитываем…' },
  'muhurta.best_hour': { en: 'Best hour by basic heuristic', ru: 'Лучший час по базовой эвристике' },
  'muhurta.score': { en: 'score', ru: 'оценка' },
  'muhurta.time': { en: 'Time', ru: 'Время' },
  'muhurta.business': { en: 'Business & Finance', ru: 'Бизнес и финансы' },
  'muhurta.marriage': { en: 'Relationships & Marriage', ru: 'Отношения и брак' },
  'muhurta.travel': { en: 'Travel & Trips', ru: 'Путешествия' },
  'muhurta.health': { en: 'Health & Procedures', ru: 'Здоровье и процедуры' },

  // AI Chat
  'chat.initial': { en: 'Namaste. I am LUMIRA. What would you like to consult the stars about today?', ru: 'Намасте. Я LUMIRA. О чем бы вы хотели спросить звезды сегодня?' },
  'chat.info_btn': { en: 'Information', ru: 'Информация' },
  'chat.placeholder': { en: 'Ask about career, relationships or current transits...', ru: 'Спросите о карьере, отношениях или текущих транзитах...' },
  'chat.you': { en: 'You', ru: 'Вы' },
  'chat.assistant': { en: 'LUMIRA', ru: 'LUMIRA' },

  // My Chart
  'chart.loading': { en: 'Calculating the math of your Destiny...', ru: 'Рассчитываем математику вашей Судьбы...' },
  'chart.error': { en: 'Error:', ru: 'Ошибка:' },
  'chart.no_profile': { en: '(Perhaps birth date is not set in profile)', ru: '(Возможно, не указана дата рождения в профиле)' },
  'chart.title': { en: 'Astronomical Coordinates (Rasi)', ru: 'Астрономические Координаты (Раси)' },
  'chart.desc': { en: 'Here are the exact planetary positions in your natal chart, calculated via Swiss Ephemeris.', ru: 'Здесь представлены точные позиции планет в вашей натальной карте, рассчитанные с помощью Swiss Ephemeris.' },
  'chart.sign': { en: 'Sign:', ru: 'Знак:' },
  'chart.nakshatra': { en: 'Nakshatra:', ru: 'Накшатра:' },
  'chart.pada': { en: 'Pada', ru: 'Пада' },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(
    (localStorage.getItem('lang') as Language) || 'ru'
  );

  const changeLanguage = (lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('lang', lang);
  };

  const t = (key: string): string => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
