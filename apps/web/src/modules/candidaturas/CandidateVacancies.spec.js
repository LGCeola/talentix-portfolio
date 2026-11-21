import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../services/api.js', () => ({ apiFetch: vi.fn() }))

const { apiFetch } = await import('../../services/api.js')
const { default: CandidateVacancies } = await import('./CandidateVacancies.vue')

const VACANCY = {
  id: 1,
  title: 'Dev Python',
  description: 'Backend',
  already_applied: false,
  criteria: [{ id: 1, name: 'Python', criterion_type: 'habilidade', weight: 100, required_level: 3 }],
}
const RESUMES = [{ id: 5, original_filename: 'cv.pdf' }]

function mockApi({ externalAnalysis, vacancies = [VACANCY] }) {
  apiFetch.mockImplementation(async (path) => {
    if (path === '/api/candidaturas/consentimento') return { external_analysis: externalAnalysis }
    if (path === '/api/vagas') return vacancies
    if (path.includes('/compatibilidade')) return { score: 80, criteria: [], suggestions: [] }
    return []
  })
}

async function openApplyForm() {
  const wrapper = mount(CandidateVacancies, { props: { resumes: RESUMES }, global: { stubs: { ConfirmationDialog: true, CriteriaBreakdown: true } } })
  await flushPromises()
  await wrapper.findAll('button').find((button) => button.text() === 'Candidatar-se').trigger('click')
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  apiFetch.mockReset()
})

describe('CandidateVacancies: consentimento', () => {
  it('cita o envio à TypeSafe quando a análise externa (Jev) está ligada', async () => {
    mockApi({ externalAnalysis: true })
    const wrapper = await openApplyForm()
    const consent = wrapper.find('.consent-text').text()
    expect(consent).toContain('recrutador desta vaga')
    expect(consent).toContain('TypeSafe')
    expect(consent).toContain('Essa autorização é necessária para se candidatar.')
  })

  it('pede só o compartilhamento com o recrutador quando ela está desligada', async () => {
    mockApi({ externalAnalysis: false })
    const wrapper = await openApplyForm()
    const consent = wrapper.find('.consent-text').text()
    expect(consent).toContain('recrutador desta vaga')
    expect(consent).not.toContain('TypeSafe')
  })
})

describe('CandidateVacancies: carregamento', () => {
  it('avisa quando não há vagas abertas', async () => {
    mockApi({ externalAnalysis: false, vacancies: [] })
    const wrapper = mount(CandidateVacancies, { props: { resumes: [] } })
    await flushPromises()
    expect(wrapper.find('.empty').text()).toBe('Nenhuma vaga aberta no momento.')
  })

  it('mostra o erro quando as vagas não carregam', async () => {
    apiFetch.mockRejectedValue(new Error('Servidor indisponível'))
    const wrapper = mount(CandidateVacancies, { props: { resumes: [] } })
    await flushPromises()
    expect(wrapper.find('.form-error').text()).toBe('Servidor indisponível')
  })
})
