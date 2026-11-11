import { levelLabel } from '../vagas/vacancy.js'

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

export const KEYWORD_MODE_NOTICE = 'Análise feita só pela busca de termos, sem o Jev: cada critério encontrado vale o peso inteiro, sem avaliar o nível.'

// Mostra como o Jev participou de cada critério; análises só com a busca não têm essa informação.
export function describeDetection(criterion) {
  const { status, source, evidence, level, confidence, required_level: required, criterion_type: type, probability } = criterion

  // Versão 3: nível estimado pelo Jev.
  if (level !== null && level !== undefined) {
    const certainty = `confiança ${Math.round(confidence * 100)}%`
    if (status === 'absent') return `Não identificado pelo Jev · ${certainty}`
    if (status === 'review' && level === 0) return `Termo encontrado, mas o Jev não identificou o critério · ${certainty}`
    const text = `Nível ${level} de ${required} exigido: ${levelLabel(type, level)}`
    return status === 'review' ? `Jev inconclusivo. ${text} · ${certainty}` : `${text} · ${certainty}`
  }

  if (probability === null || probability === undefined) {
    return status === 'review' ? 'Jev indisponível: verifique manualmente' : ''
  }
  // Versão 2, de candidaturas antigas: probabilidade de o critério estar presente.
  const percent = `${Math.round(probability * 100)}%`
  if (status === 'review') {
    return evidence ? `Termo encontrado, mas o Jev indicou ausência: ${percent}` : `Jev inconclusivo: ${percent}`
  }
  if (status === 'absent') return `Não identificado pelo Jev: ${percent}`
  return source === 'keyword' ? `Termo encontrado · Jev: ${percent}` : `Identificado pelo Jev: ${percent}`
}

export function formatPoints(points) {
  return Number(points).toLocaleString('pt-BR', { maximumFractionDigits: 1 })
}

export function splitSuggestions(text) {
  return text ? text.split('\n') : []
}

export function formatScore(score) {
  return score === null || score === undefined ? 'Análise pendente' : `${Math.round(score)} / 100`
}
