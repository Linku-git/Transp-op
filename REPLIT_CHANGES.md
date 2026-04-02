# Replit Agent Changes Log

> This file documents all changes made by Replit Agent for Claude Code to review.
> Do NOT delete this file. Claude Code will process it in the next session.

## Summary
- Total files modified: 5
- Categories: Replit initialization, configuration, host/proxy setup

---

## Changes

### [2026-04-02 20:20] Config: Vite server config updated for Replit environment
- **Files:** `frontend/vite.config.ts`
- **What:** Changed server port from 5173 to 5000, set host to 0.0.0.0, added `allowedHosts: 'all'`, added API proxy forwarding `/api` to `http://localhost:8000`
- **Why:** Replit requires port 5000 for webview; the proxy is an iframe so all hosts must be allowed; API calls need to be proxied through Vite so they work under the Replit domain
- **Before:** `port: 5173, host: true`
- **After:** `port: 5000, host: '0.0.0.0', allowedHosts: 'all', proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }`
- **Risk:** Low

### [2026-04-02 20:20] Config: API client base URL updated to use relative path
- **Files:** `frontend/src/api/client.ts`
- **What:** Changed `baseURL` from `'http://localhost:8000'` to `''` (empty string)
- **Why:** In Replit's proxied iframe environment, the browser cannot directly access `localhost:8000`. Requests now use relative URLs which are proxied through Vite to the backend.
- **Before:** `baseURL: 'http://localhost:8000'`
- **After:** `baseURL: ''`
- **Risk:** Low

### [2026-04-02 20:20] Config: Backend CORS settings updated for Replit
- **Files:** `backend/app/main.py`
- **What:** Changed `allow_origins` from `["http://localhost:5173"]` to `["*"]` and `allow_credentials` from `True` to `False`
- **Why:** In Replit's proxied environment, the origin varies. Wildcard origins are safe for dev; credentials can't be used with wildcard origins per CORS spec.
- **Before:** `allow_origins=["http://localhost:5173"], allow_credentials=True`
- **After:** `allow_origins=["*"], allow_credentials=False`
- **Risk:** Low (development only)

### [2026-04-02 20:20] Init: Backend .env created for Replit
- **Files:** `backend/.env`
- **What:** Created `.env` file from `.env.example` with Replit PostgreSQL connection strings using asyncpg driver and correct Replit DB host (`helium`)
- **Why:** Replit provides `DATABASE_URL` as plain PostgreSQL URL; backend requires asyncpg driver URL for async SQLAlchemy
- **Risk:** Low

### [2026-04-02 20:20] Init: Backend startup script created
- **Files:** `start_backend.sh`
- **What:** Created shell script to start Redis (daemonized) and uvicorn backend, with explicit environment variable exports to override Replit's system `DATABASE_URL`
- **Why:** Replit's managed `DATABASE_URL` uses plain psycopg2 dialect; backend needs `postgresql+asyncpg://` driver prefix for async SQLAlchemy
- **Risk:** Low

---

## Infrastructure Setup Performed

- PostgreSQL database: provisioned via Replit (host: helium, db: heliumdb)
- PostGIS extension: enabled (`CREATE EXTENSION IF NOT EXISTS postgis`)
- pg_trgm extension: enabled (`CREATE EXTENSION IF NOT EXISTS pg_trgm`)
- Redis: installed via Nix system packages
- Python packages: installed from `backend/requirements.txt`
- Node packages: installed from `frontend/package.json`
- Database migrations: ran all 15 Alembic migrations successfully (up to `e5f6a7b8c9d0_add_kpi_snapshot`)
- Backend workflow: running on port 8000 (console)
- Frontend workflow: running on port 5000 (webview)
- Health check: `GET /api/v1/health` returns `{"status":"healthy","db":true,"redis":true}`
