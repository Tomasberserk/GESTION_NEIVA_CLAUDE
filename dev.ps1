param(
    [string]$Command = "menu"
)

function Write-Ok      { param($msg) Write-Host "  [OK]    $msg" -ForegroundColor Green }
function Write-Info    { param($msg) Write-Host "  [>>]    $msg" -ForegroundColor Cyan }
function Write-Warn    { param($msg) Write-Host "  [WARN]  $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "  [FAIL]  $msg" -ForegroundColor Red }
function Write-Header  { param($msg) Write-Host "" ; Write-Host "=== $msg ===" -ForegroundColor Magenta }

# Verificar entorno virtual
if (-not (Test-Path ".\.venv")) {
    Write-Err "No se encontro la carpeta .venv."
    Write-Info "Asegurate de estar en la raiz del proyecto y de haber creado el entorno virtual."
    exit 1
}

# Mostrar menu interactivo si no se pasa parametro o se pide el menu
if ($Command -eq "menu") {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Magenta
    Write-Host "     GESTION NEIVA - PANEL DE CONTROL DE DESARROLLO       " -ForegroundColor White -BackgroundColor Magenta
    Write-Host "==========================================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Selecciona una opcion para arrancar tu entorno:" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [1] Levantar entorno completo (DB + Backend + Frontend)" -ForegroundColor Cyan
    Write-Host "  [2] Iniciar solo Backend (FastAPI)" -ForegroundColor Cyan
    Write-Host "  [3] Iniciar solo Frontend (Vite)" -ForegroundColor Cyan
    Write-Host "  [4] Iniciar solo Base de Datos (Docker Compose)" -ForegroundColor Cyan
    Write-Host "  [5] Aplicar migraciones de Base de Datos (Alembic)" -ForegroundColor Cyan
    Write-Host "  [6] Cargar datos iniciales de prueba (Seed)" -ForegroundColor Cyan
    Write-Host "  [7] Ejecutar pruebas de seguridad (Pytest)" -ForegroundColor Cyan
    Write-Host "  [8] Ejecutar pruebas de estres y carga (Locust)" -ForegroundColor Cyan
    Write-Host "  [9] Detener contenedores de Base de Datos" -ForegroundColor Cyan
    Write-Host "  [10] Ver ayuda de comandos de linea" -ForegroundColor Yellow
    Write-Host "  [0] Salir" -ForegroundColor Red
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Magenta
    Write-Host ""
    
    $choice = Read-Host "  Ingresa el numero de tu opcion [0-10]"
    Write-Host ""

    switch ($choice) {
        "1" { $Command = "dev" }
        "2" { $Command = "backend" }
        "3" { $Command = "frontend" }
        "4" { $Command = "db" }
        "5" { $Command = "migrate" }
        "6" { $Command = "seed" }
        "7" { $Command = "test" }
        "8" { $Command = "stress" }
        "9" { $Command = "stop" }
        "10" { $Command = "help" }
        "0" { exit 0 }
        default {
            Write-Err "Opcion no valida. Saliendo..."
            exit 1
        }
    }
}

if ($Command -eq "help") {
    Write-Host ""
    Write-Host "  Gestion Neiva - CLI de Desarrollo" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Uso directo por linea de comandos:" -ForegroundColor Gray
    Write-Host "    .\dev.ps1 [comando]" -ForegroundColor White
    Write-Host ""
    Write-Host "  Comandos disponibles:" -ForegroundColor Gray
    Write-Host "    menu      Abre este panel de control interactivo (Opción por defecto)" -ForegroundColor White
    Write-Host "    dev       Levanta TODO en paralelo (Base de datos + API + Web App)" -ForegroundColor White
    Write-Host "    backend   Arranca el servidor uvicorn con hot-reload" -ForegroundColor White
    Write-Host "    frontend  Arranca el servidor de Vite en modo desarrollo" -ForegroundColor White
    Write-Host "    db        Levanta los contenedores Docker de PostgreSQL y Redis" -ForegroundColor White
    Write-Host "    migrate   Aplica las últimas migraciones Alembic pendientes" -ForegroundColor White
    Write-Host "    seed      Puebla la base de datos con información de prueba" -ForegroundColor White
    Write-Host "    test      Ejecuta la suite de pruebas unitarias y de integración" -ForegroundColor White
    Write-Host "    stress    Ejecuta el servidor web de pruebas de carga Locust" -ForegroundColor White
    Write-Host "    stop      Detiene y remueve los contenedores Docker" -ForegroundColor White
    Write-Host ""
}
elseif ($Command -eq "dev") {
    Write-Header "Levantando Entorno de Desarrollo Completo"

    Write-Info "Intentando iniciar base de datos local con Docker..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { 
        Write-Warn "No se pudo iniciar Docker Compose. Si estas usando una base de datos remota (como Supabase en tu .env), esto es completamente normal y puedes continuar."
    }
    else {
        Write-Ok "Servicios de Base de Datos locales listos y corriendo"
    }

    Write-Info "Ejecutando migraciones Alembic..."
    .\.venv\Scripts\alembic upgrade head
    if ($LASTEXITCODE -ne 0) { 
        Write-Warn "Hubo un problema al aplicar migraciones. Verifica el estado de la DB." 
    }
    else { 
        Write-Ok "Estructura de Base de Datos al dia" 
    }

    Write-Info "Abriendo servidor Backend en ventana independiente..."
    $backendCmd = "cd '$PWD'; .\.venv\Scripts\uvicorn app.main:app --reload"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

    Write-Info "Abriendo servidor Frontend en ventana independiente..."
    $frontendCmd = "cd '$PWD\frontend'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

    Write-Host ""
    Write-Ok "Backend disponible en:  http://localhost:8000/docs"
    Write-Ok "Frontend disponible en: http://localhost:5173"
    Write-Host ""
}
elseif ($Command -eq "backend") {
    Write-Header "Iniciando Servidor API FastAPI"
    Write-Info "Ejecutando en puerto 8000 con recarga automatica..."
    .\.venv\Scripts\uvicorn app.main:app --reload
}
elseif ($Command -eq "frontend") {
    Write-Header "Iniciando Servidor de Desarrollo Vite"
    Set-Location frontend
    npm run dev
    Set-Location ..
}
elseif ($Command -eq "db") {
    Write-Header "Iniciando Base de Datos Docker"
    docker compose up -d
    if ($LASTEXITCODE -eq 0) { 
        Write-Ok "PostgreSQL y Redis en ejecucion" 
    }
    else { 
        Write-Err "Fallo al iniciar servicios de Docker" 
    }
}
elseif ($Command -eq "migrate") {
    Write-Header "Aplicando Migraciones Alembic"
    .\.venv\Scripts\alembic upgrade head
    if ($LASTEXITCODE -eq 0) { 
        Write-Ok "Migraciones de base de datos aplicadas exitosamente" 
    }
    else { 
        Write-Err "Fallo al correr las migraciones" 
    }
}
elseif ($Command -eq "seed") {
    Write-Header "Poblando Base de Datos con Datos de Prueba"
    .\.venv\Scripts\python seed.py
    if ($LASTEXITCODE -eq 0) { 
        Write-Ok "Base de datos poblada con registros de prueba con exito" 
    }
    else { 
        Write-Err "Error al ejecutar el script de seed" 
    }
}
elseif ($Command -eq "test") {
    Write-Header "Ejecutando Suite de Pruebas Unitarias y de Integracion"
    Write-Info "Configurando PYTHONPATH y ejecutando Pytest..."
    $env:PYTHONPATH = $PWD.Path
    .\.venv\Scripts\pytest tests/
    if ($LASTEXITCODE -eq 0) { 
        Write-Ok "Todas las pruebas pasaron satisfactoriamente!" 
    }
    else { 
        Write-Err "Algunas pruebas fallaron. Revisa el log de salida superior." 
    }
}
  elseif ($Command -eq "stress") {
      Write-Header "Iniciando Pruebas de Carga y Estres con Locust"
      Write-Info "Asegurate de tener el backend corriendo en http://localhost:8000"
      Write-Info "Ejecutando Locust sobre tests/stress/locustfile.py..."
      Write-Info "Abre tu navegador en http://localhost:8089 para iniciar la simulacion."
      .\.venv\Scripts\locust -f tests/stress/locustfile.py
  }
  elseif ($Command -eq "stop") {
      Write-Header "Deteniendo Servicios Docker"
      docker compose down
      if ($LASTEXITCODE -eq 0) { 
          Write-Ok "Contenedores apagados y removidos" 
      }
      else { 
          Write-Warn "No se pudieron detener todos los contenedores." 
      }
  }
else {
    Write-Err "Comando '$Command' no reconocido."
    Write-Info "Ejecuta '.\dev.ps1 help' para ver la lista de comandos disponibles."
    exit 1
}
