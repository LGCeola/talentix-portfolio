"""Traduz os critérios não encontrados ou abaixo do nível exigido em sugestões de melhoria, sem IA generativa (RF06)."""

from apps.backend.algorithm.score_calculator import CriterionResult, CriterionStatus

_MISSING = {
  "habilidade": 'Se você tem "{name}", cite essa habilidade no currículo com um exemplo de uso.',
  "experiencia": 'Se você tem experiência em "{name}", descreva onde atuou e por quanto tempo.',
  "formacao": 'Se você tem "{name}", inclua o curso e a instituição na sua formação.',
}
_BELOW_LEVEL = {
  "habilidade": 'A vaga pede mais experiência com "{name}": se você já usou em projetos ou no trabalho, descreva onde e como.',
  "experiencia": 'A vaga pede mais experiência em "{name}": se você já atuou nisso no trabalho, descreva suas responsabilidades.',
  "formacao": 'A vaga pede uma formação mais avançada em "{name}": se você tem, inclua o curso e a instituição.',
}


def build_suggestions(results: list[CriterionResult]) -> list[str]:
  pending = [result for result in results if result.status != CriterionStatus.PRESENT or result.points < result.weight]
  # Os critérios de maior peso vêm primeiro, por terem mais impacto na nota.
  pending.sort(key=lambda result: (-result.weight, result.name))
  return [_template(result).format(name=result.name) for result in pending]


def _template(result: CriterionResult) -> str:
  templates = _MISSING if result.status != CriterionStatus.PRESENT else _BELOW_LEVEL
  return templates[result.criterion_type]
