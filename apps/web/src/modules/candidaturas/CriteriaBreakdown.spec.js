import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CriteriaBreakdown from './CriteriaBreakdown.vue'

const criteria = [
  { name: 'Python', criterion_type: 'habilidade', weight: 40, required_level: 5, status: 'present', points: 24, source: 'jev', level: 3, confidence: 0.97, evidence: 'API REST em Python' },
  { name: 'SQL', criterion_type: 'habilidade', weight: 30, required_level: 3, status: 'review', points: 0, source: 'jev', level: 3, confidence: 0.6, evidence: null },
  { name: 'Computação', criterion_type: 'formacao', weight: 30, required_level: 3, status: 'absent', points: 0, source: 'jev', level: 0, confidence: 1, evidence: null },
]

describe('CriteriaBreakdown', () => {
  it('mostra status, pontos, nível estimado e evidência de cada critério', () => {
    const wrapper = mount(CriteriaBreakdown, { props: { criteria } })
    const items = wrapper.findAll('.criteria-results > li')

    expect(items).toHaveLength(3)
    expect(items[0].text()).toContain('Encontrado')
    expect(items[0].text()).toContain('24 de 40 pontos')
    expect(items[0].find('.detection').text()).toBe('Nível 3 de 5 exigido: Aplicou em projeto · confiança 97%')
    expect(items[0].find('.evidence').text()).toContain('API REST em Python')
    expect(items[1].find('.criterion-status').classes()).toContain('review')
    expect(items[2].text()).toContain('Não encontrado')
  })

  it('só mostra o aviso de revisão na tela do recrutador', () => {
    expect(mount(CriteriaBreakdown, { props: { criteria } }).find('.review-hint').exists()).toBe(false)

    const recruiter = mount(CriteriaBreakdown, { props: { criteria, reviewHint: true } })
    expect(recruiter.findAll('.review-hint')).toHaveLength(1)
    expect(recruiter.find('.review-hint').text()).toContain('confira no currículo original')
  })

  it('avisa quando a análise foi só por busca de termos', () => {
    expect(mount(CriteriaBreakdown, { props: { criteria, mode: 'levels' } }).find('.mode-notice').exists()).toBe(false)
    expect(mount(CriteriaBreakdown, { props: { criteria, mode: 'keywords' } }).find('.mode-notice').text()).toContain('sem o Jev')
  })

  it('lista as sugestões de melhoria quando existem', () => {
    expect(mount(CriteriaBreakdown, { props: { criteria } }).find('.suggestions').exists()).toBe(false)
    const wrapper = mount(CriteriaBreakdown, { props: { criteria, suggestions: ['Cite SQL', 'Inclua a formação'] } })
    expect(wrapper.findAll('.suggestions li').map((item) => item.text())).toEqual(['Cite SQL', 'Inclua a formação'])
  })
})
