import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const push = vi.fn()

vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))

const { default: RegisterPage } = await import('./RegisterPage.vue')

const stubs = { RouterLink: { template: '<a><slot /></a>' } }

function respond(ok, body) {
  return Promise.resolve({ ok, json: () => Promise.resolve(body) })
}

// Passo 1: escolhe o perfil e avança para o formulário.
async function openForm(type = 'candidate') {
  const wrapper = mount(RegisterPage, { global: { stubs } })
  const index = type === 'candidate' ? 0 : 1
  await wrapper.findAll('.type-card')[index].trigger('click')
  await wrapper.find('.submit-button').trigger('click')
  return wrapper
}

async function fill(wrapper, { name = 'Ana Silva', email = 'ana@exemplo.com', password = 'Senha-123' } = {}) {
  await wrapper.find('#name').setValue(name)
  await wrapper.find('#email').setValue(email)
  await wrapper.find('#password').setValue(password)
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

beforeEach(() => {
  push.mockClear()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('RegisterPage', () => {
  it('só avança depois de escolher o perfil', async () => {
    const wrapper = mount(RegisterPage, { global: { stubs } })
    expect(wrapper.find('.submit-button').attributes('disabled')).toBeDefined()

    await wrapper.findAll('.type-card')[1].trigger('click')
    await wrapper.find('.submit-button').trigger('click')

    expect(wrapper.find('h2').text()).toBe('Dados do recrutador')
  })

  it('cria a conta e abre o login com a confirmação', async () => {
    const fetch = vi.fn(() => respond(true, { id: 1 }))
    vi.stubGlobal('fetch', fetch)
    const wrapper = await openForm('candidate')

    await fill(wrapper)

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      name: 'Ana Silva', email: 'ana@exemplo.com', password: 'Senha-123', user_type: 'candidate',
    })
    expect(push).toHaveBeenCalledWith({ name: 'Login', query: { registered: '1' } })
  })

  it.each([
    [{ name: '' }, 'Preencha o nome, o e-mail e a senha.'],
    [{ email: 'ana@exemplo' }, 'Informe um e-mail válido.'],
    [{ password: 'curta' }, 'A senha deve ter no mínimo 8 caracteres.'],
  ])('valida %o sem chamar a API', async (fields, message) => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    const wrapper = await openForm()

    await fill(wrapper, fields)

    expect(wrapper.find('.form-error').text()).toBe(message)
    expect(fetch).not.toHaveBeenCalled()
  })

  it('mostra o erro da API, inclusive os de validação (422)', async () => {
    vi.stubGlobal('fetch', vi.fn(() => respond(false, { detail: [{ msg: 'Value error, Nome inválido' }] })))
    const wrapper = await openForm()

    await fill(wrapper)

    expect(wrapper.find('.form-error').text()).toBe('Nome inválido')
    expect(push).not.toHaveBeenCalled()
  })

  it('mostra a força da senha', async () => {
    const wrapper = await openForm()
    await wrapper.find('#password').setValue('Senha-123')
    expect(wrapper.find('.strength-label').text()).toBe('Forte')
  })
})
