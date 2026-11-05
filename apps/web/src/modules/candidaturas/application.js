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

// Mostra como o Jev participou de cada critério; análises só com a busca não têm essa informação.
export function describeDetection({ status, source, evidence, probability }) {
  if (probability === null || probability === undefined) {
    return status === 'review' ? 'Jev indisponível: verifique manualmente' : ''
  }
  const percent = `${Math.round(probability * 100)}%`
  if (status === 'review') {
    return evidence ? `Termo encontrado, mas o Jev indicou ausência: ${percent}` : `Jev inconclusivo: ${percent}`
  }
  if (status === 'absent') return `Não identificado pelo Jev: ${percent}`
  return source === 'keyword' ? `Termo encontrado · Jev: ${percent}` : `Identificado pelo Jev: ${percent}`
}

export function splitSuggestions(text) {
  return text ? text.split('\n') : []
}

export function formatScore(score) {
  return score === null || score === undefined ? 'Análise pendente' : `${Math.round(score)} / 100`
}
