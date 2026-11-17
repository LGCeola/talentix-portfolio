import { describe, expect, it } from 'vitest'
import { DEFAULT_REQUIRED_LEVEL, REQUIRED_LEVELS, evenWeights, levelLabel, requiredLevelText, totalWeight, weightText } from './vacancy.js'

describe('levelLabel', () => {
  it('usa a escala de prática para habilidade e experiência', () => {
    expect(levelLabel('habilidade', 1)).toBe('Citado no currículo')
    expect(levelLabel('experiencia', 4)).toBe('Uso profissional')
  })

  it('usa a escala própria para formação', () => {
    expect(levelLabel('formacao', 3)).toBe('Graduação concluída')
    expect(levelLabel('formacao', 5)).toBe('Mestrado ou doutorado')
  })

  it('trata o nível 0 e níveis desconhecidos', () => {
    expect(levelLabel('habilidade', 0)).toBe('Não encontrado')
    expect(levelLabel('habilidade', 9)).toBe('')
  })
})

describe('textos do requisito', () => {
  it('descreve o peso como parte da nota e o nível pelo nome', () => {
    expect(weightText({ weight: 100 })).toBe('vale 100% da nota')
    expect(requiredLevelText({ criterion_type: 'habilidade', required_level: 4 })).toBe('exige: Uso profissional')
    expect(requiredLevelText({ criterion_type: 'formacao', required_level: 3 })).toBe('exige: Graduação concluída')
  })
})

describe('níveis exigidos', () => {
  it('vão de 1 a 5, com 3 como padrão', () => {
    expect(REQUIRED_LEVELS).toEqual([1, 2, 3, 4, 5])
    expect(DEFAULT_REQUIRED_LEVEL).toBe(3)
  })
})

describe('evenWeights', () => {
  it('divide 100% em partes inteiras que sempre somam 100', () => {
    expect(evenWeights(1)).toEqual([100])
    expect(evenWeights(2)).toEqual([50, 50])
    expect(evenWeights(3)).toEqual([34, 33, 33])
    expect(evenWeights(7)).toEqual([15, 15, 14, 14, 14, 14, 14])
    for (let count = 1; count <= 30; count++) {
      expect(evenWeights(count).reduce((sum, weight) => sum + weight, 0)).toBe(100)
    }
  })

  it('não cria pesos sem requisitos', () => {
    expect(evenWeights(0)).toEqual([])
  })
})

describe('totalWeight', () => {
  it('soma os pesos e ignora valores vazios ou inválidos', () => {
    expect(totalWeight([{ weight: 40 }, { weight: 60 }])).toBe(100)
    expect(totalWeight([{ weight: 40 }, { weight: '' }, { weight: 'abc' }])).toBe(40)
    expect(totalWeight([])).toBe(0)
  })
})
