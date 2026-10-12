# Независимый приёмочный аудит LUMIRA (Acceptance Audit)

**Дата проведения:** 12 октября 2026  
**Окружение:** macOS (Apple Silicon), Docker Compose, PostgreSQL 15, Redis 7, Python 3.14 (.venv), Node.js (Vite)  
**Коммит HEAD:** `cbe9da2` (`docs: record successful full-stack CI verification`)  
**Итоговый статус приёмки:** **ГОТОВО** (все 6 обязательных критериев подтверждены реальными командами и логами)

---

## 1. Проверка Git и отсутствие секретов в diff

### Команды:
```bash
git status
git log -n 1 --oneline
git diff
```

### Фактический результат:
- **Ветка:** `main`, синхронизирована с `origin/main` (`cbe9da2`).
- **Изменённые файлы:**
  - `.gitignore` (добавлено `backups/`)
  - `backend/api/auth.py` (генерация UUID до INSERT, устранение конфликта RLS при регистрации)
  - `backend/tests/conftest.py` (сохранение схемы БД после прогона тестов вместо разрушительного drop_all на teardown, выдача SELECT ON ALL TABLES для lumira_admin_role)
  - `docker-compose.yml` (параметризация порта бэкенда `${BACKEND_PORT:-8000}:8000`, безопасные дефолты `${VAR:-}`)
- **Аудит секретов в diff:** В `git diff` отсутствуют какие-либо пароли, токены или закрытые ключи. Все конфигурационные значения ссылаются на переменные окружения.
- **Код возврата:** `0`.

---

## 2. Проверка исключения `.env` и резервных копий из Git

### Команда:
```bash
git check-ignore -v .env .env.backup.* backups/lumira_db_backup_* backups/
```

### Фактический вывод:
```text
.gitignore:2:.env	.env
.gitignore:3:.env.*	.env.backup.20261012_201745
.gitignore:3:.env.*	.env.backup.20261012_202829
.gitignore:7:backups/	backups/lumira_db_backup_20261012_202829.dump
.gitignore:7:backups/	backups/
```
- **Результат:** `.env`, все резервные копии `.env.backup.*`, каталог `backups/` и дамп `lumira_db_backup_20261012_202829.dump` надёжно исключены из контроля версий правилами `.gitignore`.
- **Код возврата:** `0`.

---

## 3. Docker Compose конфигурация, контейнеры и Health Endpoints

### Команды:
```bash
docker compose config --quiet
docker compose ps
curl -s http://127.0.0.1:8001/api/health
curl -s -I http://127.0.0.1:5173
```

### Фактический результат:
1. `docker compose config --quiet` -> код возврата `0` (ошибок нет, переменные валидны).
2. `docker compose ps`:
   - `lumira-db-1`: `postgres:15-alpine` — **Up (healthy)**, порт `127.0.0.1:5433->5432/tcp`
   - `lumira-redis-1`: `redis:7-alpine` — **Up (healthy)**, порт `127.0.0.1:6380->6379/tcp`
   - `lumira-backend-1`: `lumira-backend` — **Up**, порт `127.0.0.1:8001->8000/tcp`
   - `lumira-frontend-1`: `lumira-frontend` — **Up**, порт `127.0.0.1:5173->5173/tcp`
3. Контейнеры сторонних проектов пользователя (`freelance-bot-backend-1`, `freelance-bot-frontend-1`, `freelance-bot-worker-1`, `freelance-bot-redis-1`, `freelance-bot-postgres-1`) **не затронуты** и продолжают работать на порту 8000.
4. HTTP Healthcheck бэкенда:
   - `GET http://127.0.0.1:8001/api/health` -> `{"status":"ok"}` (**HTTP 200**).
5. HTTP доступность фронтенда:
   - `GET http://127.0.0.1:5173` -> **HTTP 200 OK**.

---

## 4. Сборка Frontend и тесты Backend

### Команды:
```bash
npm --prefix frontend run build
DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5433/${DB_NAME}" \
JWT_SECRET="${JWT_SECRET}" \
PYTHONPATH=. ./.venv/bin/pytest backend/tests/ tests/
```

### Фактический результат:
1. **Frontend build (`tsc && vite build`):**
   - Время сборки: **767ms**.
   - Ошибки компиляции TypeScript: **0**.
   - Код возврата: **0**.
2. **Backend Pytest suite:**
   - Запущено тестов: **52**.
   - Результат: **52 passed, 0 failed in 7.27s**.
   - Проверены: `test_admin_rls.py`, `test_astro.py`, `test_billing_checkout.py`, `test_billing_portal.py`, `test_billing_provider_fail_closed.py`, `test_chat_usage_timezone.py`, `test_config_security.py`, `test_life_areas_calculation.py`, `test_panchanga_labels.py`, `test_phase4.py`, `test_phase5.py`, `test_profile_validation.py`, `test_rls.py`, `test_security_and_health.py`, `test_deps.py`.
   - Код возврата: **0**.

---

## 5. Проверка прав PostgreSQL-ролей и Redis Healthcheck

### Команда:
```bash
# Проверка флагов ролей и RLS таблиц
./.venv/bin/python -c '
import asyncpg, asyncio
from dotenv import dotenv_values
cfg = dotenv_values(".env")
async def run():
    conn = await asyncpg.connect(host="127.0.0.1", port=5433, user=cfg["DB_USER"], password=cfg["DB_PASSWORD"], database=cfg["DB_NAME"])
    roles = await conn.fetch("SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin, rolbypassrls FROM pg_roles WHERE rolname IN (\x27lumira\x27, \x27lumira_app\x27, \x27lumira_admin_role\x27, \x27app_user\x27) ORDER BY rolname;")
    for r in roles: print(r)
    tables = await conn.fetch("SELECT tablename, tableowner, rowsecurity FROM pg_tables WHERE schemaname = \x27public\x27 ORDER BY tablename;")
    for t in tables: print(t)
    await conn.close()
asyncio.run(run())
'

# Проверка health Redis и DB
docker inspect lumira-redis-1 --format 'Redis Health: {{.State.Health.Status}}, FailingStreak: {{.State.Health.FailingStreak}}'
docker inspect lumira-db-1 --format 'DB Health: {{.State.Health.Status}}, FailingStreak: {{.State.Health.FailingStreak}}'
```

### Фактический результат:
1. **Привилегии ролей:**
   - `app_user`: `SUPER=False`, `CREATEROLE=False`, `CREATEDB=False`, `LOGIN=False`, `BYPASSRLS=False`
   - `lumira`: `SUPER=False`, `CREATEROLE=True`, `CREATEDB=True`, `LOGIN=True`, `BYPASSRLS=False`
   - `lumira_admin_role`: `SUPER=False`, `CREATEROLE=False`, `CREATEDB=False`, `LOGIN=True`, `BYPASSRLS=False`
   - `lumira_app`: `SUPER=False`, `CREATEROLE=False`, `CREATEDB=False`, `LOGIN=True`, `BYPASSRLS=False`
   - Ни одна роль приложения не является `SUPERUSER` и не имеет `BYPASSRLS`.
2. **Владельцы таблиц и статус RLS:**
   - Все 7 таблиц (`interaction_logs`, `memories`, `profiles`, `stripe_webhook_events`, `subscriptions`, `tenants`, `users`) принадлежат пользователю `lumira`.
   - `rowsecurity=True` активирован для всех таблиц с данными тенантов.
3. **Статус здоровья Redis и PostgreSQL:**
   - `Redis Health: healthy, FailingStreak: 0`
   - `DB Health: healthy, FailingStreak: 0`

---

## 6. E2E проверка регистрации, авторизации и RLS-изоляции тенантов

Проведён независимый тест на живом API `http://127.0.0.1:8001` и базе данных (скрипт `scratch/verify_rls_isolation.py`).

### Шаги и фактические результаты:
1. **Регистрация Пользователя A (Alice):**
   - Запрос: `POST /api/auth/register`
   - Ответ: **HTTP 200 OK**, выдан токен, тенант `8ffef57f-da4f-4b24-b8a6-2f371f649d37`, user `2f32568d-cf32-4f15-8ff2-070571d7470a`.
2. **Авторизация Пользователя A:**
   - Запрос: `POST /api/auth/token`
   - Ответ: **HTTP 200 OK**.
3. **Создание и чтение профиля Пользователя A:**
   - `POST /api/profile/me` с токеном A -> **HTTP 200 OK** (создан профиль `"Alice in Wonderland"`).
   - `GET /api/profile/me` с токеном A -> **HTTP 200 OK** (возвращён `"Alice in Wonderland"`).
4. **Регистрация Пользователя B (Bob):**
   - Запрос: `POST /api/auth/register`
   - Ответ: **HTTP 200 OK**, выдан токен, тенант `912d45e9-45c9-43b2-b75e-bdd48f76893b`, user `a6c1eb92-f251-4a4b-9bae-2f62a698e311`.
   - Подтверждено: **Tenant A (`8ffef57f-...`) != Tenant B (`912d45e9-...`)**.
5. **Проверка изоляции до создания профиля B:**
   - `GET /api/profile/me` с токеном B -> **HTTP 200 OK**, тело ответа: `null`.
   - Доказано: Пользователь B **не видит** данные профиля Пользователя A.
6. **Создание и чтение профиля Пользователя B:**
   - `POST /api/profile/me` с токеном B -> **HTTP 200 OK** (создан профиль `"Bob the Builder"`).
   - `GET /api/profile/me` с токеном B -> **HTTP 200 OK** (возвращён только `"Bob the Builder"`).
7. **Повторная проверка Пользователя A:**
   - `GET /api/profile/me` с токеном A -> **HTTP 200 OK** (возвращён только `"Alice in Wonderland"`).
8. **Прямая SQL-проверка под ролью `lumira_app`:**
   - `SET app.current_tenant = '8ffef57f-...'` -> `SELECT count(*)` возвращает ровно 1 запись (Alice).
   - `SET app.current_tenant = '912d45e9-...'` -> `SELECT count(*)` возвращает ровно 1 запись (Bob).
   - `UPDATE profiles SET name = 'hacked' WHERE tenant_id = '912d45e9-...'` в контексте Тенанта A -> затронуто **0 строк** (`UPDATE 0`, операция заблокирована RLS).
   - `DELETE FROM profiles WHERE tenant_id = '912d45e9-...'` в контексте Тенанта A -> затронуто **0 строк** (`DELETE 0`, операция заблокирована RLS).
   - `RESET app.current_tenant; SELECT count(*) FROM profiles;` -> затронуто **0 строк** (без контекста тенанта данные не видны).

---

## 7. Оставшиеся ограничения

1. **Stripe Billing:** Для локального dev биллинг работает в режиме fail-closed (HTTP 503 "Billing service is not configured"). Для тестирования оплаты требуются валидные тестовые ключи Stripe в `.env`.
2. **Telegram Bot:** Сервис запускается только при указании профиля `docker compose --profile telegram up -d bot` и требует реальный токен Telegram Bot API от `@BotFather`.
3. **Внешние AI-провайдеры:** При отсутствии активных ключей `LLM_API_KEY` или `OPENROUTER_API_KEY` запросы гороскопа и брифинга переключаются на штатные fallback-заглушки согласно архитектуре Фазы 4.
