# LUMIRA 🌌

**LUMIRA** — интеллектуальная open-source платформа ведической астрологии (Джйотиш), сочетающая детерминированные астрологические вычисления с интерпретационными возможностями современных больших языковых моделей (LLM).

Платформа построена на архитектуре multi-tenant с аппаратной изоляцией данных на уровне PostgreSQL Row-Level Security (RLS) и предоставляет интерактивный дашборд, расчет натальных карт, ежедневные брифинги и диалоговый AI-интерфейс.

---

## 🚀 Возможности платформы

* **Детерминированный Astrology Engine:**
  * Точные расчеты положений 9 грах (планет), 12 бхав (домов), асцендента и лунных стоянок (накшатр) на базе швейцарских эфемерид (`pyswisseph`) с сидерическим зодиаком и айянамшей Лахири.
  * Расчет Панчанги (Титхи, Вара, Накшатра, Йога, Карана).
  * **Принцип Source-of-Truth:** LLM никогда не производит математических расчетов планет — модель получает строго валидированные астрологические координаты и занимается исключительно контекстной интерпретацией.
* **Интерактивная натальная карта:**
  * Визуализация карты в североиндийском стиле (Diamond chart) на SVG.
  * Таблицы планетных позиций, статусов (экзальтация, падение, ретроградность) и аспектов.
* **AI-астролог и Daily Briefing:**
  * Персонализированный ежедневный астрологический брифинг на основе текущих транзитов и натальной карты.
  * Диалоговый AI-чат с сохранением контекста и защитой от галлюцинаций.
  * Поддержка OpenRouter (Llama, Claude, Mistral) и Google Gemini API с автоматическим переходом на локальный fallback при отсутствии ключей.
* **Безопасность и Multi-Tenancy:**
  * Полная изоляция организаций/пользователей через PostgreSQL `FORCE ROW LEVEL SECURITY`.
  * Разделение пулов соединений: обычное приложение работает под непривилегированной ролью `lumira_app`, административная панель использует выделенную роль `lumira_admin_role` без `SUPERUSER` и `BYPASSRLS`.
  * Аутентификация JWT (HS256) с обязательной привязкой к `tenant_id`.
  * Телеметрия запросов с `X-Correlation-ID`, замером времени отклика и маскированием чувствительных данных.
* **Административная панель:**
  * Мониторинг потребления AI токенов, количества пользователей и активности в разрезе тенантов.

---

## 🛠 Технологический стек

* **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React (Glassmorphism Dark Theme).
* **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (asyncio + asyncpg), Pydantic v2.
* **Astrology:** `pyswisseph` (Swiss Ephemeris C-bindings).
* **Database & Cache:** PostgreSQL 15+, Redis 7.
* **AI Providers:** OpenRouter API / Google Gemini API.
* **Bot:** `aiogram` 3.x (Telegram Bot).

---

## 📋 Требования

* **Docker & Docker Compose** (рекомендуется для быстрого старта)
* **Или локальное окружение:**
  * Python 3.11 или 3.12
  * Node.js 18+ и npm
  * PostgreSQL 15+
  * Redis 7+

---

## ⚙️ Настройка окружения (`.env`)

1. Скопируйте шаблон переменных окружения:
   ```bash
   cp .env.example .env
   ```

2. Сгенерируйте надежный секретный ключ JWT (не менее 32 символов):
   ```bash
   openssl rand -hex 32
   ```
   Вставьте полученное значение в переменную `JWT_SECRET` в `.env`.

3. Настройте доступы к базе данных:
   * `DB_USER` и `DB_PASSWORD`: административные учетные данные PostgreSQL (для создания таблиц и ролей).
   * `APP_DB_USER` и `APP_DB_PASSWORD`: учетные данные непривилегированной роли приложения (по умолчанию `lumira_app`).
   * `ADMIN_DB_USER` и `ADMIN_DB_PASSWORD`: учетные данные административной роли RLS (по умолчанию `lumira_admin_role`).
   * `DATABASE_URL`: строка подключения приложения (`postgresql+asyncpg://...`).
   * `ADMIN_DATABASE_URL`: строка подключения для админ-панели.

4. (Опционально) Настройте AI-провайдеры:
   * `OPENROUTER_API_KEY`: ключ от OpenRouter для доступа к моделям.
   * `LLM_API_KEY`: ключ Google Gemini API.
   * *Если ключи не указаны, приложение автоматически переключается на встроенный mock-генератор, не блокируя работу интерфейса.*

5. (Опционально) Настройте Telegram-бота:
   * `TELEGRAM_BOT_TOKEN`: токен бота, полученный у `@BotFather`.

---

## 🚀 Быстрый запуск через Docker Compose

### 1. Локальная разработка

Перед запуском обязательно заполните секреты в `.env`: `DB_PASSWORD`, `APP_DB_PASSWORD`, `ADMIN_DB_PASSWORD`, `REDIS_PASSWORD` и `JWT_SECRET`. Compose намеренно не подставляет известные пароли по умолчанию. Для локальной разработки можно сгенерировать JWT через `openssl rand -hex 32`.

Compose автоматически дождётся готовности PostgreSQL, создаст таблицы и включит политики RLS отдельным одноразовым сервисом `init-db`, а затем запустит backend и frontend. Запустите стек:

```bash
docker compose up --build
```

* **Frontend:** [http://localhost:5173](http://localhost:5173)
* **Backend API:** [http://localhost:8000](http://localhost:8000)
* **Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

*(Порты БД `5433` и Redis `6380` привязаны строго к интерфейсу `127.0.0.1` для локальной безопасности).*

### 2. Production сборка

Перед запуском production-конфигурации задайте уникальные сильные значения для всех секретов в `.env`. Не используйте значения из примеров и не публикуйте `.env`. Production Compose предоставляет HTTP на порту 80; настройте HTTPS на внешнем reverse proxy (Nginx, Caddy или Cloudflare).

Production Compose также автоматически инициализирует схему до запуска API. Первый запуск создаёт пустую базу и таблицы; для последующих обновлений схемы используйте миграции проекта, если они добавлены. Перед запуском убедитесь, что `ADMIN_EMAIL` и `ADMIN_PASSWORD` заданы, а все пароли и `JWT_SECRET` заменены на уникальные значения.

Для production-окружения используйте:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 💻 Локальный запуск без Docker

### 1. База данных и роли

Убедитесь, что PostgreSQL 15 запущен. Выполните скрипт инициализации ролей:

```bash
bash backend/database/init-user-db.sh
```

### 2. Установка и запуск Backend

```bash
# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r backend/requirements.txt

# Создание таблиц и активация RLS
python -m backend.scripts.init_tables

# Создание первого системного администратора
python backend/scripts/create_admin.py admin@example.com "SuperSecurePassword123!"

# Запуск FastAPI сервера
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Установка и запуск Frontend

```bash
cd frontend
npm install
npm run dev
```

Фронтенд запустится на [http://localhost:5173](http://localhost:5173).

---

## 🤖 Запуск Telegram-бота

Telegram-бот работает как фоновый сервис в режиме long-polling:

```bash
python -m backend.bot.main
```

---

## 🧪 Тестирование и верификация

Проект покрыт автоматическими тестами, включая сквозные RLS-тесты под реальными ролями PostgreSQL:

```bash
# Запуск полного набора тестов
DATABASE_URL="postgresql+asyncpg://lumira:lumira_password@127.0.0.1:5433/lumira_db" \
JWT_SECRET="lumira_test_secret_32_characters_long_min!" \
PYTHONPATH=. pytest backend/tests/ tests/
```

Проверка сборки фронтенда:

```bash
cd frontend
npm run build
```

---

## ⚠️ Известные ограничения и статус модулей

В соответствии с принципом прозрачности open-source разработки:

1. **Мухурта (Muhurta):**
   * В текущей версии раздел представлен как демонстрационный UI-интерфейс (mock). Движок автоматического подбора астрологически благоприятных интервалов находится в разработке.
2. **Биллинг (Billing & Subscriptions):**
   * Модель подписок и лимитов реализована на уровне API и интерфейса. Внешние платежные шлюзы (Stripe/ЮKassa) используют безопасные заглушки без реального списания средств.
3. **Telegram-бот:**
   * Бот использует long-polling соединение (`aiogram`), поэтому требует постоянно работающего серверного процесса (не подходит для serverless-платформ без постоянного рантайма).
4. **Production Web:**
   * Перед открытием публичного доступа настройте Reverse Proxy (Nginx, Caddy или Cloudflare) для терминации HTTPS/TLS и защиты от DDoS.

---

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
