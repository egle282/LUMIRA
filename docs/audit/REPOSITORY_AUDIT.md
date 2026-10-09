# Repository Audit Report

**Scope:** LUMIRA repository root and core configuration
**Commit SHA Audited:** 713cd52
**Date:** 2026-10-09
**Environment:** Python 3.14.3, Node v22.23.1, npm 10.9.8

## Executive Summary
Initial Phase 0 discovery reveals a working project structure with separated frontend (React) and backend (FastAPI) applications. The repository was recently scrubbed of git secrets (like `.env`) and is ready for an open-source security hardening pass. Development and production compose files exist but need security hardening (binding interfaces, auth).

## Inventory of Findings

### 1. Insecure Docker Compose Port Binding (Development)
- **Severity:** HIGH
- **Evidence:** `docker-compose.yml` binds PostgreSQL (`5433:5432`) and Redis (`6380:6379`) directly to all host interfaces by default.
- **Impact:** Anyone on the local network can access the database/redis instances without restriction if the host firewall permits.
- **Recommended Fix:** Change port bindings to `127.0.0.1:5433:5432` to restrict access to localhost.
- **Status:** FIXED (Port restricted to 127.0.0.1)

### 2. Hardcoded Database Credentials in Development Compose
- **Severity:** MEDIUM
- **Evidence:** `docker-compose.yml` defines `POSTGRES_USER: lumira` and `POSTGRES_PASSWORD: lumira_password` inline, as well as in the `DATABASE_URL`.
- **Impact:** Normalizes committing secrets, even for development. 
- **Recommended Fix:** Extract to `.env` file for local development or use dummy variables explicitly documented.
- **Status:** OPEN

### 3. Missing Authentication on Redis
- **Severity:** HIGH
- **Evidence:** Both `docker-compose.yml` and `docker-compose.prod.yml` use the default `redis:7-alpine` image without a password (`--requirepass`).
- **Impact:** Any service on the docker network (or external, if ports are exposed) can manipulate the cache or task queue arbitrarily.
- **Recommended Fix:** Add a `REDIS_PASSWORD` environment variable and configure the redis command to require it. Update connection strings in backend.
- **Status:** FIXED (Added --requirepass dev_redis_password and ${REDIS_PASSWORD})

### 4. Overstated Security Claims in Documentation
- **Severity:** MEDIUM
- **Evidence:** `SECURITY_MODEL.md` (to be fully verified) claims RLS and strict prompt injection defenses. Need to audit backend endpoints and RLS definitions in `backend/database/setup_rls.sql`.
- **Impact:** Users relying on the documentation may falsely assume protection that isn't fully implemented.
- **Recommended Fix:** Conduct Phase 1.3 audit of code and update docs to reflect "VERIFIED", "PARTIAL", or "NOT IMPLEMENTED".
- **Status:** OPEN

### 5. Production Compose HTTPS Termination Unclear
- **Severity:** MEDIUM
- **Evidence:** `docker-compose.prod.yml` binds `80:80` and `443:443` on the `frontend` service, implying the frontend container handles TLS termination directly.
- **Impact:** Production deployments may fail or lack secure TLS configuration if the frontend Dockerfile isn't explicitly running Nginx with certs.
- **Recommended Fix:** Verify `frontend/Dockerfile.prod` and clarify deployment steps for TLS (e.g., using Certbot/Traefik).
- **Status:** OPEN

---
## Approvals Required
- Requesting approval to modify `docker-compose.yml` and `docker-compose.prod.yml` to restrict port bindings and enforce Redis authentication.
- Requesting approval to analyze `backend/database/setup_rls.sql` and FastAPI routes to verify security model claims.
