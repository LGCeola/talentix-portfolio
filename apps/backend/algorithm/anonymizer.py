"""Remove dados pessoais identificáveis antes de enviar um currículo a um serviço externo (LGPD)."""

import re

from apps.backend.algorithm.keyword_matcher import normalize_with_positions

_PLACEHOLDER = "[removido]"
_MIN_NAME_PART_LENGTH = 3
_PATTERNS = [
  re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),  # e-mail
  re.compile(r"(?:https?://|www\.)\S+|\b(?:linkedin\.com|github\.com)/\S+", re.IGNORECASE),  # links de perfil
  re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),  # CPF
  re.compile(r"\b\d{5}-?\d{3}\b"),  # CEP
  re.compile(r"(?:\+?55[\s.-]?)?\(?\b\d{2}\)?[\s.-]?9?\d{4}[\s.-]?\d{4}\b"),  # telefone
  re.compile(r"\b\d{2}/\d{2}/\d{4}\b"),  # data completa, como a de nascimento
]


def redact(text: str, private_terms: tuple[str, ...] = ()) -> str:
  for pattern in _PATTERNS:
    text = pattern.sub(_PLACEHOLDER, text)
  return _redact_names(text, private_terms)


def _redact_names(text: str, private_terms: tuple[str, ...]) -> str:
  parts = {
    part
    for term in private_terms
    for part in normalize_with_positions(term)[0].split()
    if len(part) >= _MIN_NAME_PART_LENGTH
  }
  if not parts:
    return text

  normalized, positions = normalize_with_positions(text)
  pattern = r"(?<![a-z0-9])(?:" + "|".join(re.escape(part) for part in sorted(parts, key=len, reverse=True)) + r")(?![a-z0-9])"
  redacted = text
  # De trás para frente, para as posições anteriores continuarem válidas.
  for match in reversed(list(re.finditer(pattern, normalized))):
    redacted = redacted[:positions[match.start()]] + _PLACEHOLDER + redacted[positions[match.end() - 1] + 1:]
  return redacted
