import { describe, expect, it } from 'vitest'
import { describeDetection, formatPoints, formatScore, splitSuggestions } from './application.js'

const base = { criterion_type: 'habilidade', required_level: 4, source: 'jev', evidence: null }

describe('describeDetection: nível estimado pelo Jev (versão 3)', () => {
  it('mostra nível, nível exigido e confiança quando o critério pontua', () => {
    const text = describeDetection({ ...base, status: 'present', level: 3, confidence: 0.97 })
    expect(text).toBe('Nível 3 de 4 exigido: Aplicou em projeto · confiança 97%')
  })

  it('usa a escala de formação', () => {
    const text = describeDetection({ ...base, criterion_type: 'formacao', required_level: 3, status: 'present', level: 3, confidence: 0.9 })
    expect(text).toContain('Graduação concluída')
  })

  it('explica a ausência', () => {
    expect(describeDetection({ ...base, status: 'absent', level: 0, confidence: 1 })).toBe('Não identificado pelo Jev · confiança 100%')
  })

  it('explica o conflito com a busca por termos', () => {
    const text = describeDetection({ ...base, status: 'review', level: 0, confidence: 1, evidence: 'Não tenho experiência com Python' })
    expect(text).toBe('Termo encontrado, mas o Jev não identificou o critério · confiança 100%')
  })

  it('explica a baixa confiança', () => {
    const text = describeDetection({ ...base, status: 'review', level: 4, confidence: 0.6 })
    expect(text).toBe('Jev inconclusivo. Nível 4 de 4 exigido: Uso profissional · confiança 60%')
  })
})

describe('describeDetection: outras análises', () => {
  it('não mostra nada na busca por termos', () => {
    expect(describeDetection({ ...base, source: 'keyword', status: 'present', level: null })).toBe('')
  })

  it('avisa quando falta a resposta do Jev', () => {
    expect(describeDetection({ ...base, status: 'review', level: null })).toBe('Jev indisponível: verifique manualmente')
  })

  it('mantém o texto das candidaturas antigas, com probabilidade (versão 2)', () => {
    expect(describeDetection({ ...base, status: 'present', probability: 0.91 })).toBe('Identificado pelo Jev: 91%')
    expect(describeDetection({ ...base, source: 'keyword', status: 'present', probability: 0.8 })).toBe('Termo encontrado · Jev: 80%')
    expect(describeDetection({ ...base, status: 'absent', probability: 0.04 })).toBe('Não identificado pelo Jev: 4%')
    expect(describeDetection({ ...base, status: 'review', probability: 0.07, evidence: 'Python' })).toBe('Termo encontrado, mas o Jev indicou ausência: 7%')
    expect(describeDetection({ ...base, status: 'review', probability: 0.5 })).toBe('Jev inconclusivo: 50%')
  })
})

describe('formatação', () => {
  it('arredonda a nota e indica análise pendente', () => {
    expect(formatScore(76.5)).toBe('77 / 100')
    expect(formatScore(0)).toBe('0 / 100')
    expect(formatScore(null)).toBe('Análise pendente')
    expect(formatScore(undefined)).toBe('Análise pendente')
  })

  it('mostra pontos com até uma casa decimal, no padrão brasileiro', () => {
    expect(formatPoints(22.5)).toBe('22,5')
    expect(formatPoints(40)).toBe('40')
  })

  it('separa as sugestões por linha', () => {
    expect(splitSuggestions('a\nb')).toEqual(['a', 'b'])
    expect(splitSuggestions('')).toEqual([])
    expect(splitSuggestions(null)).toEqual([])
  })
})
