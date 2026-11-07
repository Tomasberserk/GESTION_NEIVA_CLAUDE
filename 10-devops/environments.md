# 10 — Environments

## Environments

| Environment | Purpose | Infrastructure | Who deploys |
|---|---|---|---|
| `local` | Development and testing | Local workstation (Port 8000 API, Port 5173 SPA, Docker Redis) | Developer manually |
| `staging` | Integration verification and e2e testing | Render Web Service + Supabase Staging DB | GitHub Actions on merge to `dev` |
| `production` | Live commercial service for stores | Render Web Service + Vercel Frontend + Supabase DB | GitHub Actions on release tag |

## Environment variables

| Variable | Description | Example / Source |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | Secret for HS256 JWT encoding | 64-char random hex string |
| `SUPERADMIN_KEY`| Secret header key for `/superadmin/*` | Private administrative key |
| `CORS_ORIGINS` | Allowed origins allowlist | `https://gestion-neiva-claude.vercel.app` |
| `AI_PROVIDER` | Default LLM provider | `gemini` or `groq` |
| `GEMINI_API_KEY`| Google Gemini API key | Google AI Studio |
| `GROQ_API_KEY` | Groq Cloud Whisper key | Groq Console |
| `ENVIRONMENT` | Runtime mode | `development`, `staging`, `production` |

## Secret injection rule

Secrets are never committed to git. In `staging` and `production`, secrets are injected
via Render and Vercel environment setting panels per [`security-policy.md`](../00-governance/security-policy.md).

---

**Related:** [`./local-setup.md`](./local-setup.md) · [`./ci-cd.md`](./ci-cd.md)
