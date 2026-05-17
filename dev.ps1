param(
    [string]$Command = "help"
)

function Write-Ok    { param($msg) Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Info  { param($msg) Write-Host "  >>  $msg" -ForegroundColor Cyan }
function Write-Warn  { param($msg) Write-Host "  !!  $msg" -ForegroundColor Yellow }
function Write-Err   { param($msg) Write-Host "  XX  $msg" -ForegroundColor Red }

if (-not (Test-Path ".\.venv")) {
    Write-Err "No encontre .venv. Ejecuta este script desde la raiz del proyecto."
    exit 1
}

if ($Command -eq "help") {
    Write-Host ""
    Write-Host "  Gestion Neiva - Script de desarrollo" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Uso: .\dev.ps1 [comando]" -ForegroundColor White
    Write-Host ""
    Write-Host "  Comandos:" -ForegroundColor Gray
    Write-Host "    dev       Levanta TODO (DB + backend + frontend)" -ForegroundColor White
    Write-Host "    backend   Solo FastAPI (uvicorn --reload)" -ForegroundColor White
    Write-Host "    frontend  Solo Vite (npm run dev)" -ForegroundColor White
    Write-Host "    db        Solo Docker Compose" -ForegroundColor White
    Write-Host "    migrate   Corre migraciones Alembic" -ForegroundColor White
    Write-Host "    seed      Carga datos de prueba" -ForegroundColor White
    Write-Host "    test      Corre pytest (sprint 5)" -ForegroundColor White
    Write-Host "    stop      Para los contenedores Docker" -ForegroundColor White
    Write-Host ""
}
elseif ($Command -eq "dev") {
    Write-Host "`n  Levantando entorno completo..." -ForegroundColor Magenta

    Write-Info "Iniciando PostgreSQL y Redis..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { Write-Err "Docker Compose fallo"; exit 1 }
    Write-Ok "Base de datos lista"

    Write-Info "Corriendo migraciones Alembic..."
    .\.venv\Scripts\alembic upgrade head
    if ($LASTEXITCODE -ne 0) { Write-Warn "Alembic tuvo un problema - revisa las migraciones" }
    else { Write-Ok "Migraciones aplicadas" }

    Write-Info "Abriendo backend en nueva ventana..."
    $backendCmd = "cd '$PWD'; .\.venv\Scripts\uvicorn app.main:app --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

    Write-Info "Abriendo frontend en nueva ventana..."
    $frontendCmd = "cd '$PWD\frontend'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

    Write-Host ""
    Write-Ok "Backend  ->  http://localhost:8000/docs"
    Write-Ok "Frontend ->  http://localhost:5173"
    Write-Host ""
}
elseif ($Command -eq "backend") {
    Write-Host "`n  Iniciando backend..." -ForegroundColor Magenta
    .\.venv\Scripts\uvicorn app.main:app --reload
}
elseif ($Command -eq "frontend") {
    Write-Host "`n  Iniciando frontend..." -ForegroundColor Magenta
    Set-Location frontend
    npm run dev
    Set-Location ..
}
elseif ($Command -eq "db") {
    Write-Host "`n  Iniciando base de datos..." -ForegroundColor Magenta
    docker compose up -d
    if ($LASTEXITCODE -eq 0) { Write-Ok "PostgreSQL y Redis corriendo" }
    else { Write-Err "Docker Compose fallo" }
}
elseif ($Command -eq "migrate") {
    Write-Host "`n  Corriendo migraciones..." -ForegroundColor Magenta
    .\.venv\Scripts\alembic upgrade head
    if ($LASTEXITCODE -eq 0) { Write-Ok "Migraciones aplicadas" }
    else { Write-Err "Error en migraciones" }
}
elseif ($Command -eq "seed") {
    Write-Host "`n  Cargando datos de prueba..." -ForegroundColor Magenta
    .\.venv\Scripts\python seed.py
    if ($LASTEXITCODE -eq 0) { Write-Ok "Datos cargados" }
    else { Write-Err "Error al cargar datos" }
}
elseif ($Command -eq "test") {
    Write-Host "`n  Tests..." -ForegroundColor Magenta
    Write-Warn "Tests pendientes para Sprint 5 (UUID PostgreSQL incompatible con SQLite in-memory)"
    Write-Info "Cuando esten listos: .\.venv\Scripts\python -m pytest tests\ -v"
}
elseif ($Command -eq "stop") {
    Write-Host "`n  Deteniendo contenedores..." -ForegroundColor Magenta
    docker compose down
    if ($LASTEXITCODE -eq 0) { Write-Ok "Contenedores detenidos" }
}
else {
    Write-Err "Comando '$Command' no reconocido."
    Write-Info "Ejecuta '.\dev.ps1 help' para ver los comandos disponibles."
    exit 1
}
