# DATABASE PLAN

## 1. Core Technology
**PostgreSQL** with Row-Level Security (RLS) to enforce strict multi-tenant isolation.

## 2. Core Schemas

### Identity & Tenants
- `Tenant`: id, name, created_at, settings.
- `User`: id, tenant_id, role, email, telegram_id, created_at.
- `Profile`: id, user_id, name, birth_date, birth_time, birth_location (lat, lon, timezone).

### Astrology Data (Calculated/Cached)
- `Chart`: id, profile_id, calculation_version, planet_positions, houses, ascendant.
- `Dasha`: id, profile_id, period_type, start_date, end_date, planet.
- `Transit`: id, profile_id, date, transiting_planet, natal_planet, aspect.

### AI & Memory
- `Interaction_Log`: id, user_id, intent, input, output, tokens_used, created_at.
- `Memory`: id, user_id, type (fact, preference, correction), content, created_at.

## 3. RLS Policies
All queries must execute within a set context of `current_tenant_id`. 
Policies will ensure that `SELECT, INSERT, UPDATE, DELETE` operations are restricted by `tenant_id`.
Service roles will bypass RLS for administrative tasks.
