export const APPLICATION_STATUS_LABELS = {
  pending: 'Aguardando avaliação',
  approved: 'Aprovada',
  rejected: 'Não selecionada',
}

export function formatScore(score) {
  return score === null || score === undefined ? 'Análise pendente' : `${Math.round(score)} / 100`
}
