# 10 — Local Setup

## Prerequisites

| Tool | Version | Verify with |
|---|---|---|
| Python | 3.11 or 3.12 | `python --version` |
| Node.js | >= 18.0 | `node --version` |
| Docker & Docker Compose | Latest | `docker compose version` |
| Git | Latest | `git --version` |

## Step-by-step setup (NFR-08: < 1 hour)

1. **Clone repository and configure environment:**
   ```bash
   cp .env.example .env
   ```
2. **Start supporting services (Redis 7):**
   ```bash
   docker compose up -d
   ```
3. **Set up Python virtual environment and dependencies:**
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate | Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Apply database migrations:**
   ```bash
   alembic upgrade head
   ```
5. **Start backend and frontend services:**
   - **Automated (One-Click):** Run `make dev` or execute `powershell ./dev.ps1`.
   - **Manual:**
     - Backend: `uvicorn app.main:app --reload --port 8000`
     - Frontend: `cd frontend && npm install && npm run dev`

## Verifying it worked

```bash
curl -i http://localhost:8000/health
```

A response of `{"status": "ok", "version": "2.0.0"}` confirms that the backend process is up,
connected to the database, and responding.

---

**Related:** [`./environments.md`](./environments.md) · [`./ci-cd.md`](./ci-cd.md)
