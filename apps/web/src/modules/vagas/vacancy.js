export const STATUS_LABELS = {
  draft: 'Rascunho',
  open: 'Publicada',
  closed: 'Encerrada',
}

export const CRITERION_TYPES = [
  { value: 'habilidade', label: 'Habilidade' },
  { value: 'experiencia', label: 'Experiência' },
  { value: 'formacao', label: 'Formação' },
]

export const CRITERION_TYPE_LABELS = Object.fromEntries(CRITERION_TYPES.map((type) => [type.value, type.label]))

export function totalWeight(criteria) {
  return criteria.reduce((sum, criterion) => sum + (Number(criterion.weight) || 0), 0)
}
