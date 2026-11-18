import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../../services/api.js', () => ({ apiFetch: vi.fn() }))

const { apiFetch } = await import('../../services/api.js')
const { default: CandidateDashboard } = await import('./CandidateDashboard.vue')

const stubs = { CandidateVacancies: true }
const RESUME = { id: 1, original_filename: 'cv.pdf', updated_at: '2026-11-10T12:00:00Z' }

async function render(resumes = []) {
  apiFetch.mockResolvedValueOnce(resumes)
  const wrapper = mount(CandidateDashboard, { global: { stubs } })
  await flushPromises()
  return wrapper
}

function pdf(name = 'cv.pdf', size = 1024) {
  const file = new File(['%PDF'], name, { type: 'application/pdf' })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

async function select(wrapper, file) {
  const input = wrapper.find('input[type="file"]')
  Object.defineProperty(input.element, 'files', { value: [file], configurable: true })
  await input.trigger('change')
  await flushPromises()
}

beforeEach(() => {
  apiFetch.mockReset()
})

describe('CandidateDashboard', () => {
  it('lista os currículos enviados ou avisa que não há nenhum', async () => {
    expect((await render()).find('.empty').text()).toBe('Nenhum currículo enviado ainda.')
    expect((await render([RESUME])).find('.resume-list').text()).toContain('cv.pdf')
  })

  it('envia o arquivo escolhido e o mostra no topo da lista', async () => {
    const wrapper = await render()
    apiFetch.mockResolvedValueOnce({ ...RESUME, id: 2, original_filename: 'novo.pdf' })

    await select(wrapper, pdf('novo.pdf'))

    const [path, options] = apiFetch.mock.calls[1]
    expect(path).toBe('/api/curriculos')
    expect(options.method).toBe('POST')
    expect(options.body.get('file').name).toBe('novo.pdf')
    expect(wrapper.find('.form-success').text()).toBe('Currículo enviado com sucesso!')
    expect(wrapper.find('.resume-list li').text()).toContain('novo.pdf')
  })

  it('aceita o arquivo arrastado para a área de envio', async () => {
    const wrapper = await render()
    apiFetch.mockResolvedValueOnce(RESUME)

    await wrapper.find('.dropzone').trigger('drop', { dataTransfer: { files: [pdf()] } })
    await flushPromises()

    expect(apiFetch).toHaveBeenCalledTimes(2)
    expect(wrapper.find('.form-success').exists()).toBe(true)
  })

  it('ignora o seletor fechado sem arquivo e o arquivo arrastado durante um envio', async () => {
    const wrapper = await render()
    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { value: [], configurable: true })
    await input.trigger('change')
    expect(apiFetch).toHaveBeenCalledTimes(1)

    let finishUpload
    apiFetch.mockReturnValueOnce(new Promise((resolve) => { finishUpload = resolve }))
    await select(wrapper, pdf('primeiro.pdf'))
    expect(wrapper.find('.dropzone').classes()).toContain('disabled')

    await wrapper.find('.dropzone').trigger('drop', { dataTransfer: { files: [pdf('segundo.pdf')] } })
    expect(apiFetch).toHaveBeenCalledTimes(2)

    finishUpload(RESUME)
    await flushPromises()
    expect(wrapper.find('.dropzone').classes()).not.toContain('disabled')
  })

  it('recusa formato e tamanho inválidos sem chamar a API', async () => {
    const wrapper = await render()

    await select(wrapper, pdf('foto.png'))
    expect(wrapper.find('.form-error').text()).toBe('Formato não suportado. Envie um arquivo PDF ou TXT.')

    await select(wrapper, pdf('grande.pdf', 6 * 1024 * 1024))
    expect(wrapper.find('.form-error').text()).toBe('O arquivo excede o limite de 5 MB.')

    expect(apiFetch).toHaveBeenCalledTimes(1)
  })

  it('mostra o erro da API no envio', async () => {
    const wrapper = await render()
    apiFetch.mockRejectedValueOnce(new Error('Arquivo corrompido'))

    await select(wrapper, pdf())

    expect(wrapper.find('.form-error').text()).toBe('Arquivo corrompido')
    expect(wrapper.find('.dropzone').classes()).not.toContain('disabled')
  })

  it('exclui um currículo da lista', async () => {
    const wrapper = await render([RESUME])
    apiFetch.mockResolvedValueOnce(null)

    await wrapper.find('button[aria-label="Excluir cv.pdf"]').trigger('click')
    await flushPromises()

    expect(apiFetch).toHaveBeenLastCalledWith('/api/curriculos/1', { method: 'DELETE' })
    expect(wrapper.find('.resume-list').exists()).toBe(false)
  })
})
