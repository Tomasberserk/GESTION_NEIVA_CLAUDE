#!/usr/bin/env python3
"""Script de Diagnóstico y Health Check del Proveedor LLM para Gestión Neiva.

Códigos de salida (Exit Codes):
  0 = HEALTHY (API key válida, modelo disponible, completion simple OK, JSON structured output OK)
  1 = CONFIGURATION_ERROR (API key ausente o configuración inválida)
  2 = PROVIDER_UNAVAILABLE (Falla de conexión, timeout o error 5xx del proveedor)
  3 = MODEL_UNAVAILABLE (El modelo configurado no está disponible en la cuenta/API)
  4 = STRUCTURED_OUTPUT_FAILURE (El modelo no genera JSON estructurado conforme al schema)
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno locales si existen
load_dotenv()

EXIT_HEALTHY = 0
EXIT_CONFIGURATION_ERROR = 1
EXIT_PROVIDER_UNAVAILABLE = 2
EXIT_MODEL_UNAVAILABLE = 3
EXIT_STRUCTURED_OUTPUT_FAILURE = 4


def check_groq(model: str) -> int:
    api_key = os.getenv("GROQ_API_KEY")
    print("\n=======================================================")
    print("           LLM PROVIDER HEALTH CHECK (GROQ)           ")
    print("=======================================================")
    print(f"Provider:              groq")
    print(f"Configured Model:      {model}")

    # 1. Verificar API Key
    if not api_key or not api_key.strip():
        print("API Key:               MISSING [FAIL]")
        print("Diagnostico:           Defina GROQ_API_KEY en .env o variables de entorno.")
        return EXIT_CONFIGURATION_ERROR

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"API Key:               PRESENT ({masked_key}) [OK]")

    # 2. Inicializar cliente e inspeccionar modelos
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        print("Groq SDK:              NOT INSTALLED (pip install groq) [FAIL]")
        return EXIT_CONFIGURATION_ERROR

    # 3. Model ID disponible
    try:
        models_page = client.models.list()
        available_models = [m.id for m in models_page.data]
    except Exception as exc:
        print(f"Models API Endpoint:   FAILED ({exc}) [FAIL]")
        return EXIT_PROVIDER_UNAVAILABLE

    print("Models API Endpoint:   CONNECTED [OK]")

    if model not in available_models:
        print(f"Model '{model}': NOT FOUND in account models [FAIL]")
        print(f"Modelos disponibles ({len(available_models)}):")
        for m in available_models[:10]:
            print(f"  - {m}")
        if len(available_models) > 10:
            print(f"  ... y {len(available_models) - 10} más.")
        return EXIT_MODEL_UNAVAILABLE

    print(f"Model Availability:    AVAILABLE [OK]")

    # 4. Simple completion
    try:
        comp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responde con una sola palabra: OK"}],
            max_tokens=10,
            temperature=0.0,
        )
        resp_text = (comp.choices[0].message.content or "").strip()
        print(f"Simple Completion:     PASS ('{resp_text}') [OK]")
    except Exception as exc:
        print(f"Simple Completion:     FAILED ({exc}) [FAIL]")
        return EXIT_PROVIDER_UNAVAILABLE

    # 5. JSON Structured Output
    try:
        test_prompt = (
            "Eres el clasificador del POS. Responde exclusivamente con un JSON:\n"
            '{"intent": "consulta_financiera", "confidence": 0.95, "slots": {"metric": "ventas_hoy"}}'
        )
        s_comp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON VÁLIDO."},
                {"role": "user", "content": test_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        content = (s_comp.choices[0].message.content or "").strip()
        data = json.loads(content)
        if not isinstance(data, dict) or "intent" not in data:
            raise ValueError(f"JSON recibido no contiene 'intent': {content}")
        print(f"Structured Output:     PASS (intent={data.get('intent')}) [OK]")
    except Exception as exc:
        print(f"Structured Output:     FAILED ({exc}) [FAIL]")
        return EXIT_STRUCTURED_OUTPUT_FAILURE

    print("-------------------------------------------------------")
    print("STATUS FINAL:          HEALTHY (EXIT CODE 0) [OK]")
    print("=======================================================\n")
    return EXIT_HEALTHY


def check_gemini(model: str) -> int:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    print("\n=======================================================")
    print("          LLM PROVIDER HEALTH CHECK (GEMINI)          ")
    print("=======================================================")
    print(f"Provider:              gemini")
    print(f"Configured Model:      {model}")

    if not api_key or not api_key.strip():
        print("API Key:               MISSING [FAIL]")
        return EXIT_CONFIGURATION_ERROR

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"API Key:               PRESENT ({masked_key}) [OK]")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_inst = genai.GenerativeModel(model)
        resp = model_inst.generate_content("Di unicamente: OK")
        print(f"Simple Completion:     PASS ('{resp.text.strip()}') [OK]")
    except Exception as exc:
        print(f"Gemini Call:           FAILED ({exc}) [FAIL]")
        if "404" in str(exc):
            return EXIT_MODEL_UNAVAILABLE
        return EXIT_PROVIDER_UNAVAILABLE

    print("-------------------------------------------------------")
    print("STATUS FINAL:          HEALTHY (EXIT CODE 0) [OK]")
    print("=======================================================\n")
    return EXIT_HEALTHY


def main() -> int:
    parser = argparse.ArgumentParser(description="Health check de integración LLM para Gestión Neiva")
    parser.add_argument("--provider", default=os.getenv("AI_PROVIDER", "groq"), help="Proveedor: groq o gemini")
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL") or os.getenv("AI_MODEL"),
        help="Modelo a validar (por defecto se toma de LLM_MODEL o default del proveedor)",
    )
    args = parser.parse_args()

    prov = (args.provider or "groq").lower().strip()
    if prov == "groq":
        model = args.model or "openai/gpt-oss-120b"
        return check_groq(model)
    elif prov == "gemini":
        model = args.model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        return check_gemini(model)
    else:
        print(f"Proveedor desconocido: '{prov}'. Use 'groq' o 'gemini'.")
        return EXIT_CONFIGURATION_ERROR


if __name__ == "__main__":
    sys.exit(main())
