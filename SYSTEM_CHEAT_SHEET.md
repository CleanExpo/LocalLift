# LocalLift System Cheat Sheet

This document serves as a central reference for the LocalLift application's architecture, functionality, development practices, and ongoing maintenance/debugging efforts.

## Table of Contents
- [1. Application Overview](#1-application-overview)
- [2. Technology Stack](#2-technology-stack)
- [3. Project Structure](#3-project-structure)
- [4. Key Configuration Files](#4-key-configuration-files)
- [5. Deployment & Maintenance Scripts](#5-deployment--maintenance-scripts)
- [6. Initial Diagnosis & Issues](#6-initial-diagnosis--issues)
- [7. Action Plan & Progress Log](#7-action-plan--progress-log)

---

## 1. Application Overview

*   **Purpose:** LocalLift is a platform designed to help local businesses improve their online presence and customer engagement.
*   **Core Features (based on `cookbook.md` and code):**
    *   Database Operations (SQLAlchemy & Supabase)
    *   User Authentication (Supabase Auth)
    *   Gamification (Points, Levels)
    *   Achievements
    *   Leaderboards
    *   Certifications/Courses
    *   Reporting
    *   Frontend Dashboard & Landing Pages

---

## 2. Technology Stack

*   **Backend:** Python (FastAPI likely, based on `cookbook.md` examples)
*   **Database:** Supabase (PostgreSQL)
*   **ORM:** SQLAlchemy (used in backend examples)
*   **Frontend Framework:** Static HTML, CSS, JavaScript (potentially using Jinja2 templates on the backend, but Vercel serves static `public/` dir)
*   **CSS:** TailwindCSS
*   **Frontend Hosting:** Vercel
*   **Backend Hosting:** Railway

---

## 3. Project Structure

*   `main.py` / `railway_entry.py`: Likely backend application entry points.
*   `public/`: Root directory served by Vercel (contains static frontend assets: HTML, CSS, JS).
    *   `public/index.html`: Main landing page.
    *   `public/login/index.html`: Login page.
    *   `public/dashboard/index.html`: Dashboard page.
    *   `public/js/`: Frontend JavaScript.
        *   `config.js`: Frontend configuration (API URLs, etc.).
        *   `main.js`: Core UI logic, currently contains problematic hardcoded credentials.
    *   `public/style.css`: Compiled TailwindCSS output.
*   `static/`: Contains static assets used by backend/templates? (e.g., `supabase-client.js`). Needs clarification.
*   `templates/`: Jinja2 HTML templates (likely used by the backend if serving dynamic pages, but Vercel config points to `public/`).
*   `core/`: Core backend logic (database, auth, config).
*   `apps/`: Feature-specific backend modules (client, admin, sales, reports, learning, etc.).
*   `tools/`: Utility and build scripts.
*   `supabase/`: Supabase project configuration and migrations.
*   `cookbook.md`: Project documentation and code recipes.

---

## 4. Key Configuration Files

*   `vercel.json`: Vercel deployment settings (rewrites, headers, output directory).
*   `railway.toml`: Railway deployment settings.
*   `.env`: Environment variables (should contain secrets like Supabase keys).
*   `public/js/config.js`: Frontend configuration (API endpoints).
*   `package.json`: Node.js dependencies (likely for TailwindCSS build).

---

## 5. Deployment & Maintenance Scripts

*(Using PowerShell syntax with `;` separator)*

*   **Tailwind Build:** `npm run build:css`
*   **Tailwind Watch:** `npm run watch:css`
*   **DB Migrations:** `npm run migrate` (Assumes this script exists and works)
*   **Commit All Changes:** `cd LocalLift; powershell -File ./commit-all-changes.ps1`
*   **Push to GitHub:** `cd LocalLift; powershell -File ./push-to-github.ps1`
*   **Deploy Frontend (Vercel):** `cd LocalLift; powershell -File ./deploy-vercel.ps1`
*   **Deploy Backend (Railway):** `cd LocalLift; powershell -File ./deploy-secure.sh` (Needs confirmation if this is the correct script vs. `deploy-railway.ps1`)

---

## 6. Initial Diagnosis & Issues

*   **Reported Issues:** Pages not loading correctly, UI/UX downgraded from previous state.
*   **Critical Finding:** Conflicting authentication logic.
    *   `public/js/main.js` contains **hardcoded developer credentials** and simulates API calls, bypassing actual backend interaction. **(Major Security Risk & Functional Blocker)**
    *   `public/login/index.html` correctly attempts to use `static/js/supabase-client.js` for Supabase authentication.
*   **Potential Related Issues:**
    *   JavaScript errors caused by the auth conflict or other issues in `main.js`.
    *   Incorrect API calls or lack thereof due to the simulated state in `main.js`.
    *   CSS issues (Tailwind build problems?) contributing to UI downgrade.
    *   **Backend API (`https://locallift-production.up.railway.app`) is confirmed DOWN / NOT FOUND.** This is the highest priority issue.
    *   Supabase connection issues (Incorrect Anon Key? Though the fallback seems present).
    *   Vercel rewrite rules potentially masking errors.

---

## 7. Action Plan & Progress Log

*   **Phase 1: Diagnosis & Information Gathering**
    *   [x] Review `cookbook.md`
    *   [x] Analyze `public/index.html`
    *   [x] Analyze `vercel.json`
    *   [x] Analyze `public/js/config.js`
    *   [x] Analyze `public/js/main.js`
    *   [x] Analyze `public/login/index.html`
    *   [x] Analyze `static/js/supabase-client.js`
    *   [x] Confirm Railway backend status (Result: Not Found / Down).
    *   [x] Analyze `main.py` (Backend structure OK).
    *   [x] Analyze `core/auth/router.py` (Backend Supabase auth OK, registration endpoint is placeholder).
    *   [x] Analyze `railway.toml` (Minimal config, relies on Procfile).
    *   [x] Analyze `Procfile` (Specifies `uvicorn railway_entry:app`).
    *   [x] Analyze `railway_entry.py` (Found critical `AttributeError` preventing app start).
*   **Phase 2: Create `SYSTEM_CHEAT_SHEET.md`**
    *   [x] Initialize cheat sheet with findings.
    *   [ ] **IN PROGRESS:** Update cheat sheet with backend diagnosis.
*   **Phase 3: Iterative Fixes, Enhancements & Documentation**
    *   [x] **FIXED:** Corrected `AttributeError` in `railway_entry.py` by re-exporting app from `main.py`.
    *   [ ] **NEXT:** Commit & Push backend fix. Advise Railway redeploy.
    *   [ ] **TODO:** Fix critical authentication conflict in `public/js/main.js` (after backend is running).
    *   [ ] **TODO:** Address page loading issues (likely related to backend/auth).
    *   [ ] **TODO:** Address UI/UX downgrades (CSS/JS).
    *   [ ] **TODO:** Implement enhancements based on `cookbook.md`.
    *   [ ] **TODO:** Continuously update this cheat sheet.
*   **Phase 4: Final Review & Deployment**
    *   [ ] **TODO:** Validate all fixes and enhancements.
    *   [ ] **TODO:** Finalize cheat sheet.
    *   [ ] **TODO:** Deploy frontend (Vercel) and backend (Railway).

---
*(Cheat Sheet content will be updated as progress is made)*
