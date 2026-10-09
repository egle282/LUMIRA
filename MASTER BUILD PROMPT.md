# LUMIRA — MASTER BUILD PROMPT

## Autonomous AI Engineering Project

Ты работаешь как **Autonomous Project Director + Principal Software Architect + AI Systems Engineer + Product Engineer** внутри **AI PROJECT OS v9**.

Твоя задача — самостоятельно провести создание продукта **LUMIRA** с нуля до production, используя установленную в проекте `.antigravity/` систему Director → Router → Context → Knowledge → Agents → QA → Reviewer → Evolution.

---

# 1. ГЛАВНАЯ ЦЕЛЬ

Создать production-ready SaaS/Telegram AI-продукт **LUMIRA** — персональную Vedic Astrology / Muhurta / AI Astrologer платформу.

LUMIRA должна объединять:

* Vedic Astrology;
* Panchanga;
* Nakshatra;
* Vimshottari Dasha;
* Transits;
* Muhurta;
* Natal Chart;
* Personal Muhurta;
* Life Areas;
* Karma Timeline;
* Destiny Matrix;
* Life Event Prediction;
* AI Astrologer;
* Daily AI Briefing;
* Astrology Memory;
* multi-tenant SaaS;
* Telegram Bot;
* Web Application;
* Admin Panel;
* Subscription/Billing;
* AI interpretation layer.

Главный принцип:

> **Astrology engine должен быть deterministic/source-of-truth layer. LLM не должен самостоятельно вычислять астрологические значения, если для этого существует deterministic engine.**

LLM отвечает прежде всего за:

* interpretation;
* explanation;
* dialogue;
* personalization;
* synthesis;
* UX;
* natural-language interaction.

---

# 2. РЕЖИМ РАБОТЫ

Ты НЕ должен пытаться сразу написать весь проект.

Работай итерациями.

Каждая итерация:

```text
UNDERSTAND
→ INSPECT
→ PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ DOCUMENT
→ UPDATE PROJECT STATE
→ RECORD EXPERIENCE
→ IDENTIFY IMPROVEMENTS
```

Перед каждой существенной задачей используй:

```bash
.antigravity/run "TASK"
```

Используй существующие:

```text
Director
Router
Context Loader
Knowledge Retrieval
Agents
Skills
Rules
Workflows
QA
Reviewer
Evolution Engine
Control Plane
```

Не создавай параллельную систему вместо существующей AI PROJECT OS.

---

# 3. ПЕРВЫЙ ШАГ — НЕ ПИСАТЬ КОД

Первое действие после запуска проекта:

### Провести Project Discovery.

Исследовать:

```text
repository
existing files
existing .antigravity
package managers
Python version
Node version
Docker
database
environment
existing integrations
existing documentation
existing tests
existing architecture
```

Затем определить:

```text
WHAT EXISTS
WHAT IS MISSING
WHAT CAN BE REUSED
WHAT MUST BE REBUILT
WHAT IS RISKY
WHAT IS UNKNOWN
```

Создать:

```text
PROJECT_STATUS.md
ARCHITECTURE.md
ROADMAP.md
DECISION_LOG.md
```

Не переписывать существующие документы без необходимости.

---

# 4. PRODUCT DEFINITION

Зафиксировать продуктовую модель.

## Core User

Основной пользователь:

* человек, интересующийся Vedic Astrology;
* пользователь, желающий персональные прогнозы;
* пользователь, планирующий важные события;
* пользователь, взаимодействующий с AI Astrologer.

Дополнительные пользователи:

* astrologer;
* expert;
* SaaS administrator;
* internal operator.

---

# 5. ОСНОВНЫЕ PRODUCT MODULES

Архитектура должна быть модульной.

Минимальные bounded contexts:

```text
Identity
Users
Tenants
Profiles
Astrology Engine
Panchanga
Natal Chart
Nakshatra
Dasha
Transit
Muhurta
Predictions
Karma
Destiny Matrix
AI Interpretation
AI Chat
Memory
Notifications
Subscriptions
Payments
Telegram
Web
Admin
Analytics
Observability
```

Не превращать всё в один giant module.

---

# 6. АРХИТЕКТУРА

Предпочтительная базовая архитектура:

```text
Frontend
    ↓
API
    ↓
Application Layer
    ↓
Domain Layer
    ↓
Astrology Engine
    ↓
Persistence
```

AI:

```text
Application
      ↓
AI Orchestrator
      ↓
Prompt / Context
      ↓
LLM Provider
      ↓
Structured Output
      ↓
Validation
```

Telegram:

```text
Telegram
   ↓
Bot Adapter
   ↓
Application Services
   ↓
Domain
```

Web и Telegram не должны содержать разную бизнес-логику.

---

# 7. ASTROLOGY ENGINE

Создать deterministic astrology core.

Использовать Swiss Ephemeris / соответствующую проверенную библиотеку.

Engine должен поддерживать:

### Birth Chart

* planetary positions;
* houses;
* ascendant;
* signs;
* nakshatras;
* divisional data where required;
* configurable ayanamsha.

### Panchanga

* Tithi;
* Vara;
* Nakshatra;
* Yoga;
* Karana.

### Dasha

* Vimshottari;
* Mahadasha;
* Antardasha;
* relevant sub-periods.

### Transits

* current planetary positions;
* transit-to-natal relationships;
* configurable interpretation rules.

### Muhurta

Создать deterministic scoring/rules engine.

Input:

```text
event_type
location
date_range
constraints
birth_data
```

Output:

```text
candidate windows
score
factors
positive factors
negative factors
explanation data
```

LLM НЕ должен генерировать score напрямую.

---

# 8. MUHURTA ENGINE

Создать extensible event registry.

Примеры:

```text
real_estate_purchase
real_estate_sale
marriage
business_start
company_registration
contract_signing
travel
moving
vehicle_purchase
important_meeting
medical_procedure
education
```

Каждое событие должно иметь:

```text
event definition
required inputs
rules
weights
constraints
scoring
explanation metadata
```

Новые типы Muhurta должны добавляться без переписывания engine.

---

# 9. AI INTERPRETATION LAYER

AI должен получать:

```text
deterministic astrology data
+
user profile
+
historical context
+
current question
+
relevant rules
+
memory
```

LLM должен вернуть structured output.

Например:

```json
{
  "summary": "...",
  "factors": [],
  "risks": [],
  "opportunities": [],
  "timing": [],
  "recommendations": [],
  "confidence": 0.0,
  "disclaimer": "..."
}
```

Добавить schema validation.

Никогда не доверять raw LLM output напрямую.

---

# 10. AI ASTROLOGER

Создать conversational AI layer.

Capabilities:

```text
birth chart questions
dasha questions
transit questions
muhurta
relationship
career
finance
life events
karma
daily guidance
```

Архитектура:

```text
User
 ↓
Intent Detection
 ↓
Context Retrieval
 ↓
Astrology Engine
 ↓
Memory
 ↓
AI Interpretation
 ↓
Response Validator
 ↓
User
```

---

# 11. ASTROLOGY MEMORY ENGINE

Создать долговременную пользовательскую память.

Разделить:

```text
facts
preferences
previous readings
important dates
questions
interpretation history
user corrections
```

Память должна быть:

```text
tenant isolated
user isolated
auditable
deletable
versioned
```

Не сохранять чувствительные данные без необходимости.

---

# 12. LIFE AREAS

Создать единый domain model:

```text
career
finance
relationships
family
health
education
travel
business
spirituality
```

Каждая область получает:

```text
current state
astrological factors
periods
transits
risks
opportunities
AI explanation
```

Важно:

> Не выдавать медицинские диагнозы, финансовые гарантии или категоричные утверждения о будущем.

---

# 13. KARMA TIMELINE

Создать timeline engine.

Input:

```text
natal factors
dasha
transits
configured interpretation rules
```

Output:

```text
timeline events
periods
themes
intensity
explanations
```

AI только интерпретирует deterministic result.

---

# 14. DESTINY MATRIX

Реализовать отдельный deterministic calculation engine.

Не смешивать его напрямую с Vedic Astrology.

Архитектура:

```text
Matrix Engine
     ↓
Matrix Result
     ↓
Interpretation Layer
```

---

# 15. LIFE EVENT PREDICTION

Не создавать fake certainty.

Система должна работать через:

```text
signals
periods
patterns
probabilistic/qualitative indicators
```

Использовать формулировки:

```text
possible
favorable period
higher activity
potential theme
worth paying attention to
```

Не:

```text
this will definitely happen
```

---

# 16. DAILY AI BRIEFING

Создать daily briefing pipeline:

```text
Scheduler
 ↓
Current Panchanga
 ↓
Transit Engine
 ↓
User Chart
 ↓
Relevant Life Areas
 ↓
AI Interpretation
 ↓
Personalized Briefing
 ↓
Telegram/Web
```

---

# 17. TELEGRAM BOT

Создать production Telegram bot.

Основные сценарии:

```text
/start
onboarding
birth data
location
daily briefing
my chart
dasha
transits
muhurta
life areas
AI astrologer
memory
subscription
settings
support
```

Использовать inline keyboards / menus.

Business logic не размещать непосредственно в Telegram handlers.

---

# 18. WEB APPLICATION

Создать premium SaaS interface.

Основные разделы:

```text
Dashboard
My Chart
Today
Muhurta
Predictions
Life Areas
Karma Timeline
Destiny Matrix
AI Astrologer
Memory
Profile
Subscription
Settings
```

UX:

* premium;
* clean;
* responsive;
* mobile-first;
* fast;
* accessible.

Не копировать чужой продукт 1:1.

---

# 19. ADMIN PANEL

Создать:

```text
users
tenants
subscriptions
payments
AI usage
LLM costs
prompts
models
feature flags
system health
logs
audit events
```

---

# 20. MULTI-TENANCY

Tenant isolation должна быть фундаментальным архитектурным принципом.

Каждая tenant-scoped entity должна иметь:

```text
tenant_id
```

Использовать DB-level isolation/RLS там, где применимо.

Обязательно протестировать:

```text
tenant A → own data
tenant A → cannot access tenant B
tenant B → own data
service role → controlled access
anonymous → denied
```

---

# 21. BILLING

Создать abstraction:

```text
BillingProvider
```

Чтобы можно было подключить:

```text
Stripe
Telegram Payments
Tinkoff / local provider
```

Не связывать domain logic напрямую с конкретным payment provider.

Обязательно:

```text
idempotency
webhook verification
payment state machine
audit trail
refund state
subscription state
```

---

# 22. OBSERVABILITY

Добавить:

```text
structured logs
request IDs
trace IDs
error tracking
AI latency
AI token usage
AI cost
database latency
queue latency
Telegram errors
payment events
```

Создать health checks:

```text
/api/health
/api/ready
```

---

# 23. AI PROVIDER ABSTRACTION

Создать:

```text
LLMProvider
```

и adapters:

```text
Gemini
OpenRouter
Qwen
fallback provider
```

Добавить:

```text
timeouts
retry
fallback
rate limit
cost tracking
structured output
model configuration
```

Модель не должна быть hardcoded по всему проекту.

---

# 24. SECURITY

Обязательно:

```text
authentication
authorization
tenant isolation
RLS
rate limiting
input validation
output validation
secret management
audit logging
webhook verification
CSRF/CORS policy
secure headers
dependency audit
```

Никогда не помещать:

```text
API keys
tokens
passwords
credentials
.env
```

в repository или AI context.

---

# 25. TESTING

Минимум:

```text
unit tests
integration tests
API tests
database tests
RLS tests
AI schema tests
AI evaluation tests
Telegram tests
payment tests
E2E tests
security tests
```

Для astrology engine создать reference test cases.

Особенно проверить:

```text
timezone
DST
location
ephemeris calculations
date boundaries
midnight
historical dates
future dates
```

---

# 26. AI EVALUATION

Создать отдельный evaluation suite.

Проверять:

```text
factual grounding
structured output
hallucination
instruction following
consistency
astrology-data fidelity
memory correctness
tenant isolation
response quality
```

AI не должен менять deterministic astrology values.

---

# 27. DATA MODEL

Спроектировать БД до масштабной реализации.

Предварительные domains:

```text
users
tenants
profiles
birth_profiles
locations
charts
planetary_positions
panchanga
dashas
transits
muhurta_requests
muhurta_results
predictions
life_areas
karma_events
matrix_results
conversations
messages
memories
subscriptions
payments
ai_usage
notifications
audit_events
```

Но окончательную схему определить после Architecture Discovery.

---

# 28. API

Создать contract-first API.

Документировать OpenAPI.

API должен иметь:

```text
versioning
pagination
error schema
request IDs
validation
auth
rate limits
idempotency where needed
```

---

# 29. DEVELOPMENT WORKFLOW

Для каждой feature:

```text
1. Task
2. Director
3. Context
4. Knowledge Retrieval
5. Architecture
6. Plan
7. Implementation
8. Tests
9. Security
10. Review
11. Documentation
12. Project State
13. Experience
14. Evolution
```

---

# 30. DEFINITION OF DONE

Feature считается завершённой только если:

```text
[ ] architecture approved
[ ] implementation complete
[ ] tests pass
[ ] security checked
[ ] contracts updated
[ ] documentation updated
[ ] observability added
[ ] reviewer passed
[ ] project state updated
[ ] experience recorded
```

---

# 31. PRODUCTION DEFINITION OF DONE

LUMIRA нельзя считать production-ready, пока не выполнено:

```text
[ ] production build
[ ] migrations tested
[ ] backups
[ ] monitoring
[ ] alerts
[ ] error tracking
[ ] rate limiting
[ ] secrets configured
[ ] domain configured
[ ] HTTPS
[ ] Telegram webhook
[ ] payment webhooks
[ ] billing tested
[ ] RLS tested
[ ] E2E tests
[ ] AI evaluation suite
[ ] SEO
[ ] legal pages
[ ] privacy
[ ] terms
[ ] 404
[ ] robots
[ ] sitemap
[ ] canonical
[ ] metadata
[ ] OG
[ ] favicon
[ ] performance audit
[ ] rollback procedure
[ ] disaster recovery procedure
```

---

# 32. AUTONOMY POLICY

Используй AI PROJECT OS v9 risk gates.

### LOW

Можно выполнять автоматически.

### MEDIUM

Автоматически + review.

### HIGH

Сначала план → затем approval.

### CRITICAL

Обязательное подтверждение человека.

Особое внимание:

```text
production
payments
auth
RLS
tenant isolation
secrets
database migrations
data deletion
deployment
```

---

# 33. SELF-EVOLUTION

После каждой значимой задачи:

```text
Experience
 ↓
Pattern Mining
 ↓
Lesson Proposal
 ↓
Evaluation
 ↓
Regression
 ↓
Promotion
```

Система может предлагать:

```text
new skill
new rule
new checklist
new workflow
new regression test
```

Но не должна самостоятельно изменять core rules без approval.

---

# 34. PROJECT STATE

После каждого крупного этапа обновлять:

```text
PROJECT STATE
```

Минимум:

```text
architecture
database
api
frontend
ai
tests
security
documentation
risks
technical debt
open proposals
```

Не придумывать значения.

Если состояние неизвестно:

```text
unknown
```

а не выдумывать процент.

---

# 35. GIT

Использовать понятные commits:

```text
feat:
fix:
refactor:
test:
docs:
security:
chore:
```

Не делать огромные неразборчивые commits.

Перед commit:

```text
tests
lint
typecheck
security checks
diff review
```

---

# 36. DOCUMENTATION

Поддерживать:

```text
README.md
ARCHITECTURE.md
PRODUCT.md
ROADMAP.md
API.md
DATABASE.md
AI.md
SECURITY.md
DEPLOYMENT.md
OPERATIONS.md
DECISION_LOG.md
PROJECT_STATUS.md
```

Документация должна отражать реальное состояние проекта.

---

# 37. ROADMAP EXECUTION

Работай по следующим фазам:

```text
PHASE 0 — DISCOVERY
PHASE 1 — FOUNDATION
PHASE 2 — ASTROLOGY CORE
PHASE 3 — USER / TENANT
PHASE 4 — AI LAYER
PHASE 5 — TELEGRAM
PHASE 6 — WEB APP
PHASE 7 — MUHURTA / PREDICTIONS
PHASE 8 — BILLING
PHASE 9 — ADMIN
PHASE 10 — QA / SECURITY
PHASE 11 — PRODUCTION
PHASE 12 — EVOLUTION
```

Не перескакивать через фундаментальные зависимости.

---

# 38. EXECUTION RULE

Начни с:

```text
PHASE 0 — DISCOVERY
```

Не начинай реализацию до формирования:

```text
PRODUCT
ARCHITECTURE
DATABASE PLAN
AI ARCHITECTURE
SECURITY MODEL
ROADMAP
```

После этого переходи к PHASE 1.

На каждой фазе:

```text
PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ DOCUMENT
→ STATE UPDATE
```

После завершения фазы сообщи:

```text
PHASE
COMPLETED
FILES CREATED
FILES CHANGED
TESTS
RISKS
DECISIONS
NEXT PHASE
```

Не спрашивай разрешение на очевидные низкорисковые действия.

Спрашивай подтверждение только там, где этого требует Risk Gate.

---

# 39. КРИТИЧЕСКОЕ ПРАВИЛО

Не имитируй выполненную работу.

Если что-то:

```text
не проверено
не запущено
не протестировано
не найдено
неизвестно
```

так и напиши.

Никаких:

```text
"готово"
```

если implementation/test/review фактически не выполнены.

---

# 40. ФИНАЛЬНЫЙ РЕЗУЛЬТАТ

Цель проекта:

```text
LUMIRA
```

должна закончить путь как:

```text
Production SaaS
+
Telegram Bot
+
Web Application
+
Astrology Engine
+
AI Astrologer
+
Muhurta Engine
+
Prediction Engine
+
Memory
+
Billing
+
Admin
+
Observability
+
Security
+
AI Evaluation
+
Self-Evolution
```

Итоговый критерий:

> **LUMIRA должна быть не демонстрационным прототипом, а поддерживаемым production-продуктом с deterministic astrology core и AI interpretation layer.**

Начинай с PHASE 0.

Сначала исследуй проект и текущую AI PROJECT OS.

**Не пиши production-код до завершения Discovery и архитектурного плана.**
