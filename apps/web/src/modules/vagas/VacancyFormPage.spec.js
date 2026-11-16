import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const push = vi.fn()
const route = { params: {} }

vi.mock('vue-router', () => ({ useRoute: () => route, useRouter: () => ({ push }) }))
vi.mock('../../services/api.js', () => ({ apiFetch: vi.fn() }))

const { apiFetch } = await import('../../services/api.js')
const { default: VacancyFormPage } = await import('./VacancyFormPage.vue')

const stubs = { AppLayout: { template: '<div><slot /></div>' }, RouterLink: { template: '<a><slot /></a>' } }

async function render() {
  const wrapper = mount(VacancyFormPage, { global: { stubs } })
  await flushPromises()
  return wrapper
}

function buttonWithText(wrapper, text) {
  return wrapper.findAll('button').find((button) => button.text().includes(text))
}

beforeEach(() => {
  route.params = {}
  push.mockClear()
  apiFetch.mockReset()
})

describe('VacancyFormPage: nova vaga', () => {
  it('começa com um requisito de nível 3 e bloqueia a publicação sem título', async () => {
    const wrapper = await render()
    expect(wrapper.find('h1').text()).toBe('Nova vaga')
    expect(wrapper.findAll('.criterion-row')).toHaveLength(1)
    expect(wrapper.findAll('.criterion-row select')[1].element.value).toBe('3')
    expect(wrapper.find('.blocker').text()).toBe('Informe um título com pelo menos 3 caracteres.')
    expect(buttonWithText(wrapper, 'Postar').attributes('disabled')).toBeDefined()
  })

  it('mostra os nomes dos níveis conforme o tipo do requisito', async () => {
    const wrapper = await render()
    const [type, level] = wrapper.findAll('.criterion-row select')
    expect(level.findAll('option')[2].text()).toContain('Aplicou em projeto')
    await type.setValue('formacao')
    expect(level.findAll('option')[2].text()).toContain('Graduação concluída')
  })

  it('explica o que falta até os pesos somarem 100%', async () => {
    const wrapper = await render()
    await wrapper.find('#title').setValue('Dev Python')
    expect(wrapper.find('.blocker').text()).toBe('Informe a descrição da vaga para publicá-la.')
    await wrapper.find('#description').setValue('Backend')
    expect(wrapper.find('.blocker').text()).toContain('Cada requisito precisa de um nome')
    await wrapper.find('.criterion-row input[type="text"]').setValue('Python')
    expect(wrapper.find('.blocker').text()).toBe('Os pesos somam 10%; ajuste para exatamente 100% para publicar.')
    expect(wrapper.find('.total').classes()).toContain('under')

    await wrapper.find('.weight-input input').setValue(100)
    expect(wrapper.find('.blocker').exists()).toBe(false)
    expect(wrapper.find('.total').classes()).toContain('complete')
  })

  it('adiciona e remove requisitos', async () => {
    const wrapper = await render()
    await buttonWithText(wrapper, 'Adicionar requisito').trigger('click')
    expect(wrapper.findAll('.criterion-row')).toHaveLength(2)
    // O novo requisito recebe o peso que falta para 100%.
    expect(wrapper.findAll('.weight-input input')[1].element.value).toBe('90')
    await wrapper.findAll('.icon-button')[0].trigger('click')
    expect(wrapper.findAll('.criterion-row')).toHaveLength(1)
    expect(wrapper.find('.blocker').text()).toBe('Informe um título com pelo menos 3 caracteres.')
  })

  it('publica a vaga com nível exigido e volta ao dashboard', async () => {
    apiFetch.mockResolvedValue({ id: 1 })
    const wrapper = await render()
    await wrapper.find('#title').setValue('Dev Python')
    await wrapper.find('#description').setValue('Backend')
    await wrapper.find('.criterion-row input[type="text"]').setValue('Python')
    await wrapper.findAll('.criterion-row select')[1].setValue(5)
    await wrapper.find('.weight-input input').setValue(100)

    await buttonWithText(wrapper, 'Postar').trigger('click')
    await flushPromises()

    const [path, options] = apiFetch.mock.calls[0]
    expect(path).toBe('/api/vagas')
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body)).toEqual({
      title: 'Dev Python',
      description: 'Backend',
      status: 'open',
      criteria: [{ name: 'Python', criterion_type: 'habilidade', required_level: 5, weight: 100 }],
    })
    expect(push).toHaveBeenCalledWith({ name: 'Dashboard' })
  })

  it('salva rascunho incompleto e mostra erros da API', async () => {
    apiFetch.mockRejectedValue(new Error('A soma dos pesos não pode passar de 100%'))
    const wrapper = await render()
    await wrapper.find('#title').setValue('Rascunho')
    await wrapper.find('.criterion-row input[type="text"]').setValue('Python')

    await buttonWithText(wrapper, 'Salvar rascunho').trigger('click')
    await flushPromises()

    expect(JSON.parse(apiFetch.mock.calls[0][1].body).status).toBe('draft')
    expect(wrapper.find('.form-error').text()).toBe('A soma dos pesos não pode passar de 100%')
    expect(push).not.toHaveBeenCalled()
  })
})

describe('VacancyFormPage: edição', () => {
  it('carrega a vaga e salva com PUT', async () => {
    route.params = { id: '7' }
    apiFetch.mockResolvedValueOnce({
      title: 'Dev',
      description: 'Backend',
      status: 'open',
      criteria: [{ name: 'Python', criterion_type: 'habilidade', required_level: 4, weight: 100 }],
    })
    const wrapper = await render()

    expect(apiFetch).toHaveBeenCalledWith('/api/vagas/7')
    expect(wrapper.find('h1').text()).toBe('Editar vaga')
    expect(wrapper.find('.status-badge').text()).toBe('Publicada')
    expect(wrapper.findAll('.criterion-row select')[1].element.value).toBe('4')
    expect(buttonWithText(wrapper, 'Salvar rascunho')).toBeUndefined()

    apiFetch.mockResolvedValueOnce({})
    await buttonWithText(wrapper, 'Salvar alterações').trigger('click')
    await flushPromises()
    expect(apiFetch.mock.calls[1][0]).toBe('/api/vagas/7')
    expect(apiFetch.mock.calls[1][1].method).toBe('PUT')
  })

  it('não permite editar vaga encerrada', async () => {
    route.params = { id: '7' }
    apiFetch.mockResolvedValueOnce({ title: 'Dev', description: 'x', status: 'closed', criteria: [] })
    const wrapper = await render()
    expect(wrapper.find('.form-error').text()).toBe('Vagas encerradas não podem ser editadas.')
    expect(buttonWithText(wrapper, 'Salvar')).toBeUndefined()
  })

  it('mostra o erro quando a vaga não carrega', async () => {
    route.params = { id: '7' }
    apiFetch.mockRejectedValueOnce(new Error('Vaga não encontrada'))
    const wrapper = await render()
    expect(wrapper.find('.form-error').text()).toBe('Vaga não encontrada')
  })
})
