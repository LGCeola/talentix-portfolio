"""Busca determinística de um critério no texto do currículo, ignorando caixa e acentos."""

import re
import unicodedata

_SNIPPET_RADIUS = 60
# Impede que "Java" case com "JavaScript" e que "C" case com "C++" ou "C#".
_BEFORE = r"(?<![a-z0-9+#])"
_AFTER = r"(?![a-z0-9+#])"


def find_evidence(text: str, term: str) -> str | None:
  """Devolve o trecho do texto original em que o termo aparece, ou None."""
  words = _normalize(term)[0].split()
  if not words:
    return None

  normalized_text, positions = _normalize(text)
  pattern = _BEFORE + r"[\s\-/]+".join(re.escape(word) for word in words) + _AFTER
  match = re.search(pattern, normalized_text)
  if not match:
    return None
  return _snippet(text, positions[match.start()], positions[match.end() - 1] + 1)


def _normalize(text: str) -> tuple[str, list[int]]:
  """Remove acentos e caixa, mantendo a posição original de cada caractere gerado."""
  characters: list[str] = []
  positions: list[int] = []
  for index, character in enumerate(text):
    for decomposed in unicodedata.normalize("NFD", character):
      if unicodedata.combining(decomposed):
        continue
      for folded in decomposed.casefold():
        characters.append(folded)
        positions.append(index)
  return "".join(characters), positions


def _snippet(text: str, start: int, end: int) -> str:
  from_index = max(0, start - _SNIPPET_RADIUS)
  to_index = min(len(text), end + _SNIPPET_RADIUS)
  snippet = " ".join(text[from_index:to_index].split())
  prefix = "..." if from_index > 0 else ""
  suffix = "..." if to_index < len(text) else ""
  return f"{prefix}{snippet}{suffix}"
