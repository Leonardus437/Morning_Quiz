---
description: Repository Information Overview
alwaysApply: true
---

# Morning Quiz System Information

## Summary
An offline-first quiz system for TVET/TSS education, designed to run on local networks without requiring internet access. The system provides quiz functionality for teachers and students with automatic grading, leaderboards, and performance reports.

## Structure
- **backend/**: FastAPI-based Python backend with database models and API endpoints
- **frontend/**: SvelteKit-based frontend with PWA support for offline functionality
- **rtb_templates/**: Templates for RTB (Results-based Teaching) integration
- **docker-compose files**: Configuration for different deployment scenarios

## Language & Runtime
**Backend**:
- **Language**: Python 3.11
- **Framework**: FastAPI 0.100.0
- **Database**: PostgreSQL 15

**Frontend**:
- **Language**: JavaScript
- **Framework**: SvelteKit 1.20.4
- **Node.js**: 18.x
- **Build Tool**: Vite 4.4.2

## Dependencies

### Backend Dependencies
- **Web Framework**: FastAPI, Uvicorn
- **Database**: SQLAlchemy, PostgreSQL
- **Authentication**: JWT, Bcrypt, Passlib
- **Document Processing**: python-docx, PyPDF2, ReportLab, OpenPyXL

### Frontend Dependencies
- **UI Framework**: Svelte 4.0.5
- **Styling**: TailwindCSS 3.3.0
- **Deployment**: @sveltejs/adapter-node 1.3.1
- **PWA Support**: Service Worker with offline caching

## Build & Installation

### Development Setup
```bash
# Start in development mode
docker-compose -f docker-compose.dev.yml up -d
```

### Production Deployment
```bash
# Start in production mode
docker-compose up -d
```

### Offline Mode
```bash
# Start in offline-only mode
docker-compose -f docker-compose.offline.yml up -d
```

## Docker
**Services**:
- **db**: PostgreSQL 15 Alpine
- **backend**: Python 3.11 with FastAPI
- **frontend**: Node.js 18 Alpine with SvelteKit

**Network Configuration**:
- Frontend exposed on port 3000
- Backend API on port 8000
- Database on port 5432

## Main Features
- **Offline-First**: Service worker caching for offline operation
- **PWA Support**: Installable on mobile devices
- **RTB Integration**: Results-based Teaching methodology integration
- **Performance Reports**: PDF/Excel export of student performance
- **Responsive Design**: Mobile-friendly interface

## Testing
**Backend Testing**:
- Manual testing scripts in repository root
- System health checks via `system_health_check.py`

**Frontend Testing**:
- Offline functionality tests via `test_offline_functionality.py`
- Network access tests via `test_network_access.html`

## Access Points
- **Teacher Panel**: http://localhost:3000/admin
- **Student Access**: http://localhost:3000
- **Default Admin**: Username: `admin` / Password: `admin123`