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

// Os níveis descrevem evidências no currículo, as mesmas usadas nas perguntas ao Jev (integrations/jev.py).
const PRACTICE_LEVELS = {
  1: 'Citado no currículo',
  2: 'Estudou (curso ou disciplina)',
  3: 'Aplicou em projeto',
  4: 'Uso profissional',
  5: 'Referência: liderou ou ensinou',
}

const EDUCATION_LEVELS = {
  1: 'Curso livre ou técnico',
  2: 'Graduação em andamento',
  3: 'Graduação concluída',
  4: 'Pós-graduação',
  5: 'Mestrado ou doutorado',
}

export const REQUIRED_LEVELS = [1, 2, 3, 4, 5]
export const DEFAULT_REQUIRED_LEVEL = 3

export function levelLabel(criterionType, level) {
  if (level === 0) return 'Não encontrado'
  return (criterionType === 'formacao' ? EDUCATION_LEVELS : PRACTICE_LEVELS)[level] ?? ''
}

export function totalWeight(criteria) {
  return criteria.reduce((sum, criterion) => sum + (Number(criterion.weight) || 0), 0)
}
