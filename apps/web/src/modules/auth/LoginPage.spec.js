import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const push = vi.fn()
const route = { query: {} }

vi.mock('vue-router', () => ({ useRoute: () => route, useRouter: () => ({ push }) }))

const { default: LoginPage } = await import('./LoginPage.vue')

const stubs = { RouterLink: { template: '<a><slot /></a>' } }

function respond(ok, body) {
  return Promise.resolve({ ok, json: () => Promise.resolve(body) })
}

async function submit(wrapper, email = 'ana@exemplo.com', password = 'senha-123') {
  await wrapper.find('#email').setValue(email)
  await wrapper.find('#password').setValue(password)
  await wrapper.find('form').trigger('submit')
  await flushPromises()
}

beforeEach(() => {
  localStorage.clear()
  push.mockClear()
  route.query = {}
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('LoginPage', () => {
  it('guarda a sessão e abre o dashboard', async () => {
    const fetch = vi.fn(() => respond(true, { access_token: 'abc', user: { name: 'Ana', user_type: 'candidate' } }))
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(LoginPage, { global: { stubs } })

    await submit(wrapper)

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ email: 'ana@exemplo.com', password: 'senha-123' })
    expect(localStorage.getItem('talentix_token')).toBe('abc')
    expect(JSON.parse(localStorage.getItem('talentix_user')).name).toBe('Ana')
    expect(push).toHaveBeenCalledWith({ name: 'Dashboard' })
  })

  it('mostra o erro da API e não guarda sessão', async () => {
    vi.stubGlobal('fetch', vi.fn(() => respond(false, { detail: 'E-mail ou senha inválidos' })))
    const wrapper = mount(LoginPage, { global: { stubs } })

    await submit(wrapper)

    expect(wrapper.find('.form-error').text()).toBe('E-mail ou senha inválidos')
    expect(localStorage.getItem('talentix_token')).toBeNull()
    expect(push).not.toHaveBeenCalled()
    expect(wrapper.find('.submit-button').text()).toBe('Entrar')
  })

  it('usa uma mensagem padrão quando a API não explica o erro', async () => {
    vi.stubGlobal('fetch', vi.fn(() => respond(false, {})))
    const wrapper = mount(LoginPage, { global: { stubs } })
    await submit(wrapper)
    expect(wrapper.find('.form-error').text()).toBe('Não foi possível entrar. Verifique os seus dados.')
  })

  it('pede para preencher os campos vazios sem chamar a API', async () => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(LoginPage, { global: { stubs } })

    await submit(wrapper, '', '')

    expect(wrapper.find('.form-error').text()).toBe('Preencha o e-mail e a senha.')
    expect(fetch).not.toHaveBeenCalled()
  })

  it('recusa e-mail mal formatado sem chamar a API', async () => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    const wrapper = mount(LoginPage, { global: { stubs } })

    await submit(wrapper, 'invalido', 'senha-123')

    expect(wrapper.find('.form-error').text()).toBe('Informe um e-mail válido, como nome@exemplo.com.')
    expect(fetch).not.toHaveBeenCalled()
  })

  it('mostra a mensagem de um erro de validação (422) em vez de [object Object]', async () => {
    vi.stubGlobal('fetch', vi.fn(() => respond(false, { detail: [{ msg: 'Value error, Senha inválida' }] })))
    const wrapper = mount(LoginPage, { global: { stubs } })

    await submit(wrapper)

    expect(wrapper.find('.form-error').text()).toBe('Senha inválida')
  })

  it('confirma o cadastro recém-criado', () => {
    route.query = { registered: '1' }
    expect(mount(LoginPage, { global: { stubs } }).find('.form-success').text()).toContain('Conta criada com sucesso')
  })

  it('mostra e esconde a senha', async () => {
    const wrapper = mount(LoginPage, { global: { stubs } })
    expect(wrapper.find('#password').attributes('type')).toBe('password')
    await wrapper.find('.show-password').trigger('click')
    expect(wrapper.find('#password').attributes('type')).toBe('text')
  })
})
