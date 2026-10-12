# LUMIRA 🌌

**LUMIRA** — интеллектуальная open-source платформа ведической астрологии (Джйотиш), сочетающая детерминированные астрологические вычисления с интерпретационными возможностями современных больших языковых моделей (LLM).

Платформа построена на архитектуре multi-tenant с аппаратной изоляцией данных на уровне PostgreSQL Row-Level Security (RLS) и предоставляет интерактивный дашборд, расчет натальных карт, ежедневные брифинги и диалоговый AI-интерфейс.

---

## 🚀 Возможности платформы

* **Детерминированный Astrology Engine:**
  * Расчёт сидерических долгот 9 грах (включая Раху и Кету), скоростей, накшатр и пад на базе Swiss Ephemeris (`pyswisseph`) с айянамшей Лахири. В модуле сфер жизни дополнительно используются асцендент и целознаковые дома; полноценная система управителей домов пока не реализована.
  * Расчет Панчанги (Титхи, Вара, Накшатра, Йога, Карана).
  * **Принцип Source-of-Truth:** LLM никогда не производит математических расчетов планет — модель получает строго валидированные астрологические координаты и занимается исключительно контекстной интерпретацией.
* **Интерактивная натальная карта:**
  * Визуализация планетных положений в североиндийском стиле (Diamond chart) на SVG.
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
   **Важно:** значения в `.env.example` — только placeholders. До запуска замените все пароли, `JWT_SECRET` и другие секреты на собственные уникальные значения. Не коммитьте `.env` в Git.

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
   * Если ключи не указаны, функции AI-интерпретации могут быть недоступны; задайте хотя бы один поддерживаемый ключ в `.env`.

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

Telegram-бот запускается отдельно, только если задан `TELEGRAM_BOT_TOKEN`:

```bash
docker compose -f docker-compose.prod.yml --profile telegram up -d --build
```

---

## 💻 Локальный запуск без Docker

### 1. База данных и роли

Убедитесь, что PostgreSQL 15 запущен, а база `lumira_db` уже создана. Скрипт создаёт роли приложения и администратора внутри существующей базы. Перед запуском загрузите настройки из `.env` в текущую оболочку и явно задайте параметры подключения для `psql`:

```bash
set -a
source .env
set +a
export POSTGRES_USER="$DB_USER"
export POSTGRES_DB="$DB_NAME"
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c 'SELECT 1'
bash backend/database/init-user-db.sh
```

Команда `psql` использует стандартный способ аутентификации PostgreSQL на вашей системе; при необходимости настройте `PGHOST`, `PGPORT` и `PGPASSWORD` перед запуском. Не храните пароль БД в истории команд.

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

# Создание первого системного администратора: вводите пароль скрыто, не вставляйте его в историю команд
read -r -p "Admin email: " ADMIN_EMAIL
read -r -s -p "Admin password: " ADMIN_PASSWORD
echo
python backend/scripts/create_admin.py "$ADMIN_EMAIL" "$ADMIN_PASSWORD"
unset ADMIN_PASSWORD

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
# Use the app-role credentials configured in your local .env.
set -a
source .env
set +a
DATABASE_URL="postgresql+asyncpg://${APP_DB_USER}:${APP_DB_PASSWORD}@127.0.0.1:5433/${DB_NAME}" \
JWT_SECRET="$(openssl rand -hex 32)" \
PYTHONPATH=. pytest backend/tests/ tests/
```

Проверка сборки фронтенда:

```bash
cd frontend
npm run build
```

---

## ⚠️ Известные ограничения и статус модулей

Текущая версия — self-hosted MVP: основные пользовательские сценарии доступны, но перед публичным production-развёртыванием необходимо настроить секреты, HTTPS, резервное копирование и мониторинг.

1. **Мухурта (Muhurta):**
   * Работает серверный почасовой скрининг Панчанги на выбранную дату с использованием сохранённых координат и часового пояса. Это эвристическая предварительная оценка, а не полный классический расчёт мухурты: не учитываются лагна на каждый интервал, Раху-кала, восход/закат и настройки конкретной традиции.
2. **Биллинг (Billing & Subscriptions):**
   * Stripe Checkout, проверка подписи webhook, обновление статуса подписки и Stripe Customer Portal реализованы. Для активации задайте `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO` и `STRIPE_PRICE_PREMIUM` и настройте в Stripe endpoint `/api/billing/webhook`. До настройки платные действия закрыты; неактивированная конфигурация не создаёт фиктивные ссылки.
   * Оплата через Telegram Stars пока не реализована.
3. **Астрологические расчёты:**
   * Натальные положения рассчитываются через Swiss Ephemeris; сферные сигналы используют целознаковые дома и Vimshottari Mahadasha. Полная трактовка управителей домов, баллов силы, дробных карт и полноценная классическая мухурта не заявляются как готовые функции.
   * Астрологические интерпретации носят традиционный символический характер и не заменяют медицинские, юридические или финансовые рекомендации.
4. **Karma Timeline и Destiny Matrix:**
   * Экспериментальные направления, не входящие в стабильный основной пользовательский поток. Не следует считать их полноценными персональными предсказательными движками.
5. **AI-провайдеры:**
   * Для AI-чата и AI-интерпретации задайте `OPENROUTER_API_KEY` и/или `LLM_API_KEY`. Без ключей детерминированные астрологические данные могут быть доступны, но LLM-интерпретация будет отключена.
6. **Telegram-бот и production Web:**
   * Telegram-бот работает через long polling и требует постоянно работающего процесса. Для публичного веб-доступа настройте HTTPS reverse proxy, безопасное хранение секретов, резервное копирование БД и мониторинг.

## 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
