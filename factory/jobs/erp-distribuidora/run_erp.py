"""Arranca uvicorn en modo desarrollo para el ERP Distribuidora con el PYTHONPATH correcto.

Uso:
    python run_erp.py
    python run_erp.py --port 8000
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de desarrollo ERP Distribuidora")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()

    # Copiamos variables de entorno y forzamos el PYTHONPATH a la raíz del ERP
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT

    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", args.host,
        "--port", args.port,
    ]
    if not args.no_reload:
        cmd.append("--reload")

    print(f"[ERP dev] PYTHONPATH={ROOT}")
    print(f"[ERP dev] Servidor ERP: http://{args.host}:{args.port}")
    print(f"[ERP dev] Docs ERP:     http://{args.host}:{args.port}/docs")
    print(f"[ERP dev] Health Check: http://{args.host}:{args.port}/\n")

    subprocess.run(cmd, env=env, cwd=ROOT)

if __name__ == "__main__":
    main()
