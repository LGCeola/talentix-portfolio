import { describe, expect, it } from 'vitest'
import { DEFAULT_REQUIRED_LEVEL, REQUIRED_LEVELS, levelLabel, totalWeight } from './vacancy.js'

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

describe('níveis exigidos', () => {
  it('vão de 1 a 5, com 3 como padrão', () => {
    expect(REQUIRED_LEVELS).toEqual([1, 2, 3, 4, 5])
    expect(DEFAULT_REQUIRED_LEVEL).toBe(3)
  })
})

describe('totalWeight', () => {
  it('soma os pesos e ignora valores vazios ou inválidos', () => {
    expect(totalWeight([{ weight: 40 }, { weight: 60 }])).toBe(100)
    expect(totalWeight([{ weight: 40 }, { weight: '' }, { weight: 'abc' }])).toBe(40)
    expect(totalWeight([])).toBe(0)
  })
})
