import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../services/api.js', () => ({ apiFetch: vi.fn() }))

const { apiFetch } = await import('../../services/api.js')
const { default: CandidateVacancies } = await import('./CandidateVacancies.vue')

function mockApi({ externalAnalysis }) {
  apiFetch.mockImplementation(async (path) => {
    if (path === '/api/candidaturas/consentimento') return { external_analysis: externalAnalysis }
    return []
  })
}

async function render() {
  const wrapper = mount(CandidateVacancies, { props: { resumes: [] }, global: { stubs: { ConfirmationDialog: true } } })
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  apiFetch.mockReset()
})

describe('CandidateVacancies', () => {
  it('avisa o painel quando a análise externa (Jev) está ligada', async () => {
    mockApi({ externalAnalysis: true })
    const wrapper = await render()
    expect(wrapper.emitted('external-analysis')).toEqual([[true]])
    expect(wrapper.find('.empty').text()).toBe('Nenhuma vaga aberta no momento.')
  })

  it('também avisa quando ela está desligada', async () => {
    mockApi({ externalAnalysis: false })
    const wrapper = await render()
    expect(wrapper.emitted('external-analysis')).toEqual([[false]])
  })

  it('mostra o erro quando as vagas não carregam, sem avisar o painel', async () => {
    apiFetch.mockRejectedValue(new Error('Servidor indisponível'))
    const wrapper = await render()
    expect(wrapper.emitted('external-analysis')).toBeUndefined()
    expect(wrapper.text()).toContain('Servidor indisponível')
  })
})
