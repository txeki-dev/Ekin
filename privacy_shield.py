"""
Escudo de Privacidad Local para Ekin Kanban.

Filtra, sanitiza y protege secretos (claves de API, credenciales, tokens y llaves privadas)
y datos de carácter personal (PII como emails) en notas, diarios y comentarios del tablero,
evitando que se expongan a agentes de IA externos (Claude Code, Antigravity, Cursor) o a la red.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


PATTERNS = {
    "private_key": re.compile(
        r"-----BEGIN (?:[A-Z0-9_-]+ )?PRIVATE KEY-----[\s\S]+?-----END (?:[A-Z0-9_-]+ )?PRIVATE KEY-----"
    ),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b"),
    "github_fine_grained": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
    # Antes que la de OpenAI: su patrón genérico «sk-» también casa con las de Anthropic
    "anthropic_key": re.compile(r"\bsk-ant-[a-zA-Z0-9_-]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[a-zA-Z0-9_-]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "slack_token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    "stripe_key": re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9\-_.~+/]{20,}\b", re.IGNORECASE),
    "url_credentials": re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*://)([^:\s/@]+):([^@\s/]+)@"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}


REPLACEMENTS = {
    "private_key": "[REDACTED_PRIVATE_KEY]",
    "github_token": "[REDACTED_GITHUB_TOKEN]",
    "github_fine_grained": "[REDACTED_GITHUB_TOKEN]",
    "anthropic_key": "[REDACTED_ANTHROPIC_API_KEY]",
    "openai_key": "[REDACTED_OPENAI_API_KEY]",
    "google_api_key": "[REDACTED_GOOGLE_API_KEY]",
    "slack_token": "[REDACTED_SLACK_TOKEN]",
    "stripe_key": "[REDACTED_STRIPE_KEY]",
    "jwt": "[REDACTED_JWT]",
    "aws_access_key": "[REDACTED_AWS_KEY]",
    "bearer_token": "[REDACTED_BEARER_TOKEN]",
    "url_credentials": r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@",
    "email": "[REDACTED_EMAIL]",
}


def sanitize_text(text: str, mask_email: bool = True) -> Tuple[str, List[Dict[str, str]]]:
    """Sanitiza el texto eliminando tokens sensibles y credenciales.
    Devuelve (texto_sanitizado, lista_de_redacciones)."""
    if not text:
        return text, []

    sanitized = text
    redactions: List[Dict[str, str]] = []

    # Prioridad: primero claves privadas multilínea, luego tokens específicos
    for pattern_name, regex in PATTERNS.items():
        if pattern_name == "email" and not mask_email:
            continue

        replacement = REPLACEMENTS[pattern_name]

        # Encontrar todas las coincidencias para auditoría
        for match in regex.finditer(sanitized):
            matched_val = match.group(0)
            redactions.append({
                "type": pattern_name,
                "preview": f"{matched_val[:4]}...{matched_val[-3:]}" if len(matched_val) > 8 else "***",
            })

        sanitized = regex.sub(replacement, sanitized)

    return sanitized, redactions


def has_sensitive_data(text: str, check_email: bool = True) -> bool:
    """Comprueba rápidamente si un texto contiene algún patrón confidencial."""
    if not text:
        return False
    for pattern_name, regex in PATTERNS.items():
        if pattern_name == "email" and not check_email:
            continue
        if regex.search(text):
            return True
    return False
