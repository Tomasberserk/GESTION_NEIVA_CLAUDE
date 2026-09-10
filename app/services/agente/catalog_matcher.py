"""Módulo de resolución y coincidencia difusa (Fuzzy Matching) de productos del catálogo.

Diseñado como interfaz desacoplada con 3 zonas de decisión:
1. AUTO_RESOLVED: Coincidencia alta con margen significativo sobre el segundo lugar.
2. NEEDS_CLARIFICATION: Coincidencias cercanas que requieren desambiguación con el usuario.
3. NOT_FOUND: Ningún producto supera el umbral mínimo aceptable.

Trata los nombres del catálogo y las consultas del usuario como datos no confiables.
"""

import os
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

# Parámetros iniciales configurables por entorno
MATCH_AUTO_MIN_SCORE = float(os.getenv("MATCH_AUTO_MIN_SCORE", "0.85"))
MATCH_AUTO_MIN_MARGIN = float(os.getenv("MATCH_AUTO_MIN_MARGIN", "0.15"))
MATCH_CLARIFY_MIN_SCORE = float(os.getenv("MATCH_CLARIFY_MIN_SCORE", "0.55"))

# Constantes de resultado
MATCH_AUTO_RESOLVED = "AUTO_RESOLVED"
MATCH_NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
MATCH_NOT_FOUND = "NOT_FOUND"


def normalizar_texto(texto: str) -> str:
    """Normaliza texto eliminando tildes, signos de puntuación y espacios redundantes."""
    if not texto:
        return ""
    # Remover tildes
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    texto = texto.lower()
    # Remover caracteres no alfanuméricos excepto espacios
    texto = re.sub(r"[^\w\s]", " ", texto)
    # Limpiar palabras vacías coloquiales comunes en tiendas
    texto = re.sub(r"\b(de|el|la|los|las|un|una|unos|unas|por|favor)\b", " ", texto)
    # Colapsar espacios
    return " ".join(texto.split())


# Mapeo de sinónimos y modismos populares en tiendas de barrio colombianas
ALIAS_TIENDA_COLOMBIA: dict[str, str] = {
    "pola": "cerveza aguila poker club colombia andina pilsen costeña",
    "polas": "cerveza aguila poker club colombia andina pilsen costeña",
    "birra": "cerveza poker aguila",
    "birras": "cerveza poker aguila",
    "gaseosita": "gaseosa coca cola postobon quatro sprite colombiana pepsi",
    "gaseositas": "gaseosa coca cola postobon quatro sprite colombiana pepsi",
    "gaseosa": "coca cola postobon quatro sprite colombiana pepsi",
    "chitos": "cheetos chitos frito lay snacks",
    "papas": "margarita lays papas fritas",
    "papitas": "margarita lays papas fritas",
    "leche": "alqueria colanta parmalat proleche",
    "arroz": "diana roa florhuila",
    "aceite": "premier diana girasol oleocali gourmet",
}


def calcular_similitud(query: str, target: str) -> float:
    """Calcula similitud difusa combinando SequenceMatcher, contención y alias colombianos."""
    q_norm = normalizar_texto(query)
    t_norm = normalizar_texto(target)

    if not q_norm or not t_norm:
        return 0.0

    if q_norm == t_norm:
        return 1.0

    ratio = SequenceMatcher(None, q_norm, t_norm).ratio()

    # Si una palabra clave completa está contenida, elevar el score base
    if q_norm in t_norm or t_norm in q_norm:
        ratio = max(ratio, 0.88)

    # Coincidencia de tokens individuales
    q_tokens = set(q_norm.split())
    t_tokens = set(t_norm.split())
    if q_tokens and t_tokens:
        token_overlap = len(q_tokens & t_tokens) / max(len(q_tokens), len(t_tokens))
        ratio = max(ratio, token_overlap * 0.9)

        # Si todos los tokens de la consulta están en el producto (ej: "arroz diana" en "arroz diana 1kg")
        if q_tokens.issubset(t_tokens):
            ratio = max(ratio, 0.88)

        # Expansión de modismos populares colombianos (P1.5)
        for tok in q_tokens:
            sinonimos = ALIAS_TIENDA_COLOMBIA.get(tok, "").split()
            if any(s in t_tokens or any(s in t_w for t_w in t_tokens) for s in sinonimos):
                ratio = max(ratio, 0.88)

    return min(ratio, 1.0)


def match_producto(
    query: str,
    productos: list[Any],
    min_auto_score: float = MATCH_AUTO_MIN_SCORE,
    min_auto_margin: float = MATCH_AUTO_MIN_MARGIN,
    min_clarify_score: float = MATCH_CLARIFY_MIN_SCORE,
) -> tuple[str, Any]:
    """
    Evalúa la consulta del usuario contra la lista de productos activos de la tienda.

    Retorna:
    - (MATCH_AUTO_RESOLVED, producto_ganador)
    - (MATCH_NEEDS_CLARIFICATION, [lista_de_candidatos_para_aclarar])
    - (MATCH_NOT_FOUND, [])
    """
    if not query or not productos:
        return MATCH_NOT_FOUND, []

    candidatos_con_score: list[tuple[float, Any]] = []

    for prod in productos:
        nombre = getattr(prod, "nombre", "")
        score = calcular_similitud(query, nombre)
        if score >= min_clarify_score:
            candidatos_con_score.append((score, prod))

    if not candidatos_con_score:
        return MATCH_NOT_FOUND, []

    # Ordenar de mayor a menor score
    candidatos_con_score.sort(key=lambda x: x[0], reverse=True)

    mejor_score, mejor_prod = candidatos_con_score[0]

    # Caso 1: Solo hay un candidato y supera el score para auto-resolver
    if len(candidatos_con_score) == 1:
        if mejor_score >= min_auto_score:
            return MATCH_AUTO_RESOLVED, mejor_prod
        else:
            return MATCH_NEEDS_CLARIFICATION, [mejor_prod]

    segundo_score, _ = candidatos_con_score[1]
    margen = mejor_score - segundo_score

    # Caso 2: El primer candidato supera el umbral y tiene margen suficiente sobre el segundo
    if mejor_score >= min_auto_score and margen >= min_auto_margin:
        return MATCH_AUTO_RESOLVED, mejor_prod

    # Caso 3: Ambigüedad -> Ofrecer top candidatos (máximo 4 opciones)
    top_candidatos = [item[1] for item in candidatos_con_score[:4]]
    return MATCH_NEEDS_CLARIFICATION, top_candidatos
