# =============================================================================
#  Gestión Neiva — Makefile de desarrollo
#  Uso: make <comando>
# =============================================================================

.PHONY: help dev backend frontend db migrate seed test lint clean

# Muestra esta ayuda por defecto
help:
	@echo ""
	@echo "  🏪 Gestión Neiva — Comandos disponibles"
	@echo ""
	@echo "  make dev        Levanta TODO el entorno (DB + backend + frontend)"
	@echo "  make backend    Solo el servidor FastAPI (uvicorn --reload)"
	@echo "  make frontend   Solo Vite (npm run dev)"
	@echo "  make db         Solo la base de datos (Docker Compose)"
	@echo "  make migrate    Corre las migraciones de Alembic"
	@echo "  make seed       Carga datos de prueba (seed.py)"
	@echo "  make test       Corre los tests con pytest"
	@echo "  make lint       Chequea el código con ruff"
	@echo "  make clean      Para los contenedores Docker"
	@echo ""

# -----------------------------------------------------------------------------
# dev: levanta DB, luego backend y frontend en paralelo
# -----------------------------------------------------------------------------
dev: db migrate
	@echo "🚀 Levantando backend y frontend..."
	@start cmd /k ".venv\Scripts\uvicorn app.main:app --reload"
	@start cmd /k "cd frontend && npm run dev"
	@echo ""
	@echo "  ✅ Backend  →  http://localhost:8000/docs"
	@echo "  ✅ Frontend →  http://localhost:5173"
	@echo ""

# -----------------------------------------------------------------------------
# Servicios individuales
# -----------------------------------------------------------------------------
backend:
	.venv\Scripts\uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

db:
	@echo "🐘 Iniciando PostgreSQL y Redis..."
	docker compose up -d
	@echo "✅ Base de datos lista"

# -----------------------------------------------------------------------------
# Migraciones y datos de prueba
# -----------------------------------------------------------------------------
migrate:
	@echo "📦 Corriendo migraciones Alembic..."
	.venv\Scripts\alembic upgrade head

seed:
	@echo "🌱 Cargando datos de prueba..."
	.venv\Scripts\python seed.py

# -----------------------------------------------------------------------------
# Calidad de código
# -----------------------------------------------------------------------------
test:
	@echo "🧪 Corriendo tests..."
	.venv\Scripts\pytest tests/ -v

lint:
	@echo "🔍 Checkeando código con ruff..."
	.venv\Scripts\ruff check app/

# -----------------------------------------------------------------------------
# Limpieza
# -----------------------------------------------------------------------------
clean:
	@echo "🛑 Deteniendo contenedores Docker..."
	docker compose down
	@echo "✅ Contenedores detenidos"
