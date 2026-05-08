"""Arranca uvicorn en modo desarrollo con el PYTHONPATH correcto.

Uso:
    python dev.py
    python dev.py --port 8001
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de desarrollo TiendApp")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default="8000")
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()

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

    print(f"[dev] PYTHONPATH={ROOT}")
    print(f"[dev] Servidor: http://{args.host}:{args.port}")
    print(f"[dev] Docs:     http://{args.host}:{args.port}/docs")
    print(f"[dev] Health:   http://{args.host}:{args.port}/health\n")

    subprocess.run(cmd, env=env, cwd=ROOT)


if __name__ == "__main__":
    main()
