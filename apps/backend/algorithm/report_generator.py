"""Traduz os critérios não encontrados em sugestões de melhoria, sem IA generativa (RF06)."""

from apps.backend.algorithm.score_calculator import CriterionResult, CriterionStatus

_TEMPLATES = {
  "habilidade": 'Se você tem "{name}", cite essa habilidade no currículo com um exemplo de uso.',
  "experiencia": 'Se você tem experiência em "{name}", descreva onde atuou e por quanto tempo.',
  "formacao": 'Se você tem "{name}", inclua o curso e a instituição na sua formação.',
}


def build_suggestions(results: list[CriterionResult]) -> list[str]:
  missing = [result for result in results if result.status != CriterionStatus.PRESENT]
  # Os critérios de maior peso vêm primeiro, por terem mais impacto na nota.
  missing.sort(key=lambda result: (-result.weight, result.name))
  return [_TEMPLATES[result.criterion_type].format(name=result.name) for result in missing]
