export const APPLICATION_STATUS_LABELS = {
  pending: 'Aguardando avaliação',
  approved: 'Aprovada',
  rejected: 'Não selecionada',
}

export const CRITERION_STATUS_LABELS = {
  present: 'Encontrado',
  absent: 'Não encontrado',
  review: 'A revisar',
}

export function splitSuggestions(text) {
  return text ? text.split('\n') : []
}

export function formatScore(score) {
  return score === null || score === undefined ? 'Análise pendente' : `${Math.round(score)} / 100`
}
