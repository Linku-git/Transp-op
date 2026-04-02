# Transpop — Plateforme d'Orchestration Mobilite RH

## Overview

Transpop is an intelligent HR mobility orchestration platform that provides companies with a fully dimensioned, secured, and financially optimized transport model. Unlike operational transport tools (SWVL, Via), Transpop intervenes **before exploitation** — delivering diagnostic, sizing, financial engineering, and journey valorization.

## Tech Stack

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 + GeoAlchemy2
- **Database:** PostgreSQL 15+ with PostGIS
- **Cache/Queue:** Redis + Celery
- **Optimization:** Google OR-Tools, scikit-learn (DBSCAN, KMeans)
- **Auth:** Auth0 / Keycloak (JWT + OAuth2)

### Frontend (Web Dashboard)
- **Framework:** React 18+ with TypeScript (strict mode)
- **Build:** Vite
- **Styling:** TailwindCSS
- **Charts:** Recharts
- **Maps:** Leaflet + react-leaflet
- **State:** Zustand
- **Testing:** Vitest + React Testing Library

### Mobile App
- **Framework:** Flutter (Dart)
- **Platforms:** iOS 15+ / Android 10+ (API 29+)
- **Maps:** Google Maps for Flutter
- **Push:** Firebase Cloud Messaging (FCM)
- **Offline:** Hive / SQLite
- **Auth:** Auth0 Flutter SDK

### Infrastructure
- **Containers:** Docker + Docker Compose (dev), Kubernetes (prod)
- **CI/CD:** GitHub Actions
- **Monitoring:** Grafana + Prometheus
- **Storage:** AWS S3 / GCP Cloud Storage
- **IaC:** Terraform

## Project Structure

```
Employee Transport Optimization/
  agents.md                          # Coding agent instructions
  Employee_Transport_Optimization_PRD_v3.md  # Product Requirements Document
  Docs/
    README.md                        # This file
    PROGRESS.md                      # Session progress tracker
    ARCHITECTURE.md                  # System architecture
    DATABASE_SCHEMA.md               # Complete database schema
    API_ENDPOINTS.md                 # All API endpoints
    FRONTEND_PAGES.md                # Web dashboard pages
    MOBILE_PAGES.md                  # Flutter app screens
    LOCAL_MOBILE_FUNCTIONALITY.md    # Offline & local storage
    ROADMAP.md                       # Development roadmap
    sessions/                        # Coding session files
      session-01.md ... session-92.md
  backend/                           # FastAPI backend (created in session-02)
  frontend/                          # React web app (created in session-03)
  mobile/                            # Flutter app (created in session-45)
  docker-compose.yml                 # Dev environment (created in session-01)
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ & npm
- Flutter 3.x SDK
- PostgreSQL 15+ with PostGIS extension

### Quick Start (Docker)
```bash
# Clone the repository
git clone <repo-url>
cd "Employee Transport Optimization"

# Start all services
docker-compose up -d

# Backend API: http://localhost:8000
# Frontend:    http://localhost:5173
# API Docs:    http://localhost:8000/docs
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Mobile
```bash
cd mobile
flutter pub get
flutter run
```

## Development Workflow

1. Read [[agents]] for coding rules and conventions
2. Check [[PROGRESS]] for current project state
3. Pick the next incomplete session from `Docs/sessions/`
4. Follow the session's atomic task list
5. Update documentation after each session (see [[agents#3. Documentation Update Requirements]])

## Modules

| Module | Description | Phase |
|--------|-------------|-------|
| A | Site Management | 1 |
| B | Employee Data Management | 1 |
| C | Modal Analysis & Usage Tracking | 1 |
| D | Optimization Engine | 1 |
| E | Financial Engineering & Fleet Arbitrage | 2 |
| F | Journey Valorization | 5 |
| RTI | Real-Time Information Guarantee | 4 |
| Security | Employee Security Module | 4 |
| RBAC | Role-Based Access Control | 0 |

## User Profiles

| Profile | Interface | Description |
|---------|-----------|-------------|
| DRH | Web Dashboard | HR Director — configures mobility, validates sizing |
| DAF | Web Dashboard | Finance Director — TCO/ROI analysis, fleet arbitrage |
| Salarie | Mobile App | Employee — trip booking, RTI, content consumption |
| Operateur | Web Portal | Transport operator — read-only sizing plans |
| Admin | Web Admin | Platform admin — users, integrations, RGPD |

## Documentation

- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Complete database schema (38 tables)
- [[API_ENDPOINTS]] — All API endpoints (~125 endpoints)
- [[FRONTEND_PAGES]] — Web dashboard pages & components
- [[MOBILE_PAGES]] — Flutter mobile app screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline capabilities & caching
- [[ROADMAP]] — Development roadmap & timeline
- [[PROGRESS]] — Session progress tracker (92 sessions)
- [[agents]] — Coding agent instructions & conventions

## License

Confidential — Internal use only.
