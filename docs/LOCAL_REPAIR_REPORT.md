# Отчёт о локальном восстановлении окружения LUMIRA (Local Repair Report)

**Дата:** 12 октября 2026  
**Окружение:** macOS (Apple Silicon), Docker Compose, PostgreSQL 15 (Docker), Redis 7 (Docker)  
**Ветка:** `main`  
**Статус готовности:** **ГОТОВО** (локальный MVP полностью запущен, проверен и протестирован)

---

## 1. Исходная причина ошибок

1. **Несогласованность переменных окружения и прерванный запуск:**
   - Предыдущий shell-скрипт аварийно завершился с кодом ошибки `127`.
   - В `.env` отсутствовали обязательные для Docker Compose переменные: `APP_DB_PASSWORD`, `ADMIN_DB_PASSWORD`, `REDIS_PASSWORD`, `DATABASE_URL`, `ADMIN_DATABASE_URL`, `REDIS_URL`.
   - Значение `DB_PASSWORD` в `.env` не совпадало с фактическим паролем роли `lumira` в существующем кластере PostgreSQL, из-за чего попытки подключения вызывали ошибку `password authentication failed`.
2. **Конфликт портов хоста:**
   - Порт `8000` на хосте был занят другим работающим Docker-проектом пользователя (`freelance-bot-backend-1`). Запуск LUMIRA напрямую на `127.0.0.1:8000` вызывал бы конфликт портов.
3. **Отсутствие ролей в кластере:**
   - В существующем томе `lumira_postgres_data` роль `lumira_app` отсутствовала. Роль `lumira_admin_role` существовала, но её пароль не был синхронизирован. Таблиц в схеме `public` не было создано.
4. **Ошибка RLS при регистрации (`InvalidRequestError / RLS policy violation`):**
   - В методе `register` (`backend/api/auth.py`) после `await db.commit()` вызывался `await db.refresh(new_user)`.
   - Контекст тенанта `app.current_tenant` устанавливался как транзакционный (`is_local = true`). После завершения транзакции коммитом контекст сбрасывался.
   - Принудительная политика `FORCE ROW LEVEL SECURITY` для не-суперпользователя скрывала вновь созданную строку при отсутствии контекста, приводя к сбою `Could not refresh instance`.
5. **Зависимости локального виртуального окружения:**
   - В `.venv` отсутствовали пакеты `google-genai` (новый SDK Gemini) и `stripe`.

---

## 2. Безопасные действия с базой данных

- **Сохранение данных и томов:** Существующий том `lumira_postgres_data` сохранён полностью. Команды `down -v`, `volume rm` или `prune` не выполнялись.
- **Резервное копирование:**
  - Создана копия `.env` с меткой времени: `.env.backup.20261012_202829` (права 0600, исключена из Git).
  - Снят дамп `pg_dump -Fc`: `backups/lumira_db_backup_20261012_202829.dump` (проверен через `pg_restore --list`).
- **Восстановление ролей:**
  - Действия выполнены от имени владельца базы `lumira` (права `CREATEROLE`, не суперпользователь).
  - Создана непривилегированная роль `lumira_app` с `NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS`.
  - Синхронизирована непривилегированная роль `lumira_admin_role` с `NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS`.
  - Назначены минимально необходимые права (`CONNECT ON DATABASE`, `USAGE ON SCHEMA public`).
- **Инициализация схемы и RLS:**
  - Запущен штатный скрипт `backend.scripts.init_tables`.
  - Созданы таблицы: `tenants`, `users`, `profiles`, `interaction_logs`, `memories`, `subscriptions`, `stripe_webhook_events`.
  - Владельцем таблиц назначен bootstrap-пользователь `lumira`.
  - Включён `FORCE ROW LEVEL SECURITY` на всех сущностях тенантов с политиками изоляции.
  - Назначены права DML для `lumira_app` и только `SELECT` для `lumira_admin_role`.

---

## 3. Роли PostgreSQL и их назначение

| Роль | Login | Права | Назначение |
|---|---|---|---|
| `lumira` | Да | `CREATEROLE`, `CREATEDB`, `NOSUPERUSER`, `NOBYPASSRLS` | Владелец БД и схемы, миграции и bootstrap |
| `lumira_app` | Да | `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOBYPASSRLS` | Основная роль приложения (FastAPI), строгое соблюдение RLS |
| `lumira_admin_role` | Да | `NOSUPERUSER`, `NOCREATEDB`, `NOCREATEROLE`, `NOBYPASSRLS` | Аналитика и кросс-тенантные отчёты (только `SELECT`, без RLS обхода) |
| `app_user` | Нет | `NOLOGIN`, `NOSUPERUSER`, `NOBYPASSRLS` | Групповая роль для наследования базовых прав |

---

## 4. Изменённые файлы

1. **`.gitignore`**
   - Добавлен каталог `backups/`, предотвращающий случайную фиксацию локальных дампов базы данных в Git.
2. **`docker-compose.yml`**
   - Порт бэкенда на хосте параметризован: `${BACKEND_PORT:-8000}:8000`.
   - В сервис `frontend` передана переменная `VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8001}`.
   - Для опциональных провайдеров (Stripe, Telegram, OpenRouter, Gemini) добавлены безопасные дефолты `${VAR:-}`, исключающие предупреждения Compose при локальной разработке.
3. **`backend/api/auth.py`**
   - Явное присвоение идентификатора `new_user.id = str(uuid.uuid4())` перед вставкой.
   - Удалён избыточный `await db.refresh(new_user)` после `commit()`, устранивший конфликт с транзакционным RLS-контекстом при регистрации.
4. **`.env`** (локальный файл, исключён из Git, права 0600)
   - Синхронизированы `DB_USER=lumira`, `DB_NAME=lumira_db`, ротирован безопасный `DB_PASSWORD`.
   - Сгенерированы безопасные пароли для `lumira_app`, `lumira_admin_role`, `redis`.
   - Заданы `BACKEND_PORT=8001` и `VITE_API_BASE_URL=http://localhost:8001` для исключения конфликта с контейнером `freelance-bot-backend-1`.

---

## 5. Проведённые проверки и фактические результаты

1. **Конфигурация Docker Compose:**
   - Команда: `docker compose config --quiet`
   - Результат: **Успешно (exit code 0)**.
2. **Проверка компиляции Python:**
   - Команда: `./.venv/bin/python -m compileall backend`
   - Результат: **Успешно (0 синтаксических ошибок)**.
3. **Запуск сервисов LUMIRA в Docker Compose:**
   - Команда: `docker compose ps`
   - Результаты:
     - `lumira-db-1`: `postgres:15-alpine` — **Up (healthy)**, порт `127.0.0.1:5433->5432`
     - `lumira-redis-1`: `redis:7-alpine` — **Up (healthy)**, порт `127.0.0.1:6380->6379`
     - `lumira-backend-1`: `lumira-backend` — **Up**, порт `127.0.0.1:8001->8000`
     - `lumira-frontend-1`: `lumira-frontend` — **Up**, порт `127.0.0.1:5173->5173`
4. **Сторонние контейнеры:**
   - Все 5 контейнеров проекта `freelance-bot` не затронуты и продолжают работать.
5. **Проверка API Health:**
   - Команда: `curl -s http://127.0.0.1:8001/api/health`
   - Ответ: `{"status":"ok"}` (**HTTP 200**).
6. **Проверка Frontend:**
   - Команда: `curl -s -I http://127.0.0.1:5173`
   - Ответ: **HTTP/1.1 200 OK**.
7. **Сборка Frontend:**
   - Команда: `npm --prefix frontend run build`
   - Результат: **Успешно (tsc + vite build за 780ms, 0 ошибок)**.
8. **E2E регистрация и авторизация пользователя через API:**
   - POST `/api/auth/register` -> **HTTP 200 OK** (возвращён bearer token, тенант и пользователь изолированы).
   - POST `/api/auth/token` -> **HTTP 200 OK** (успешная аутентификация).
9. **Полный набор тестов pytest:**
   - Команда: `DATABASE_URL="..." JWT_SECRET="..." PYTHONPATH=. ./.venv/bin/pytest backend/tests/ tests/`
   - Результат: **52 passed, 0 failed in 7.42s**.

---

## 6. Шаги для повторного запуска

Для запуска проекта в штатном режиме:
```bash
# Запуск сервисов базы данных, кэша, бэкенда и фронтенда
docker compose up -d

# Проверка статуса сервисов
docker compose ps

# Проверка логов бэкенда
docker compose logs --tail=50 backend

# Остановка сервисов (БЕЗ удаления томов)
docker compose down
```

Для локального запуска бэкенда вне Docker:
```bash
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

---

## 7. Известные ограничения

- **Stripe Billing:** Локально биллинг работает в режиме fail-closed (возвращает 503 "Billing service is not configured"). Для тестирования реальных платежей требуются валидные тестовые ключи Stripe в `.env`.
- **Telegram Bot:** Сервис бота выделен в отдельный compose profile `["telegram"]` и не стартует по умолчанию без `docker compose --profile telegram up -d bot` и действующего токена Telegram Bot API.
- **Внешние AI-модели:** При отсутствии активных ключей `LLM_API_KEY` или `OPENROUTER_API_KEY` запросы гороскопа и брифинга переключаются на штатные fallback-заглушки согласно архитектуре Фазы 4.
