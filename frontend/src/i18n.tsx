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

  // Settings
  'settings.language': { en: 'Language', ru: 'Язык' },
  'settings.logout': { en: 'Logout', ru: 'Выйти из аккаунта' },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(
    (localStorage.getItem('lang') as Language) || 'en'
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
