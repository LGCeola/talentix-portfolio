import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const push = vi.fn()
const USER = { name: 'Ana', email: 'ana@exemplo.com', user_type: 'candidate' }

vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('../../services/api.js', () => ({
  apiFetch: vi.fn(),
  clearSession: vi.fn(),
  getCurrentUser: () => USER,
  saveCurrentUser: vi.fn(),
}))

const { apiFetch, clearSession } = await import('../../services/api.js')
const { default: AccountPage } = await import('./AccountPage.vue')

// Dialog simplificado: mostra o conteúdo só quando aberto e expõe os botões.
const DialogStub = {
  props: ['modelValue', 'loading'],
  emits: ['update:modelValue', 'confirm'],
  template: `<div v-if="modelValue" class="dialog">
    <slot />
    <button class="dialog-confirm" @click="$emit('confirm')">Excluir</button>
    <button class="dialog-cancel" @click="$emit('update:modelValue', false)">Voltar</button>
  </div>`,
}

async function mountPage() {
  apiFetch.mockResolvedValueOnce(USER)
  const wrapper = mount(AccountPage, {
    global: { stubs: { AppLayout: { template: '<div><slot /></div>' }, RouterLink: true, ConfirmationDialog: DialogStub } },
  })
  await flushPromises()
  return wrapper
}

async function requestDeletion(wrapper) {
  await wrapper.find('#delete-password').setValue('senha-123')
  await wrapper.find('.confirm-check input').setValue(true)
  await wrapper.find('.danger-zone form').trigger('submit')
}

beforeEach(() => {
  apiFetch.mockReset()
  clearSession.mockClear()
  push.mockClear()
})

describe('AccountPage - excluir conta', () => {
  it('pede confirmação antes de excluir', async () => {
    const wrapper = await mountPage()

    await requestDeletion(wrapper)

    expect(wrapper.find('.dialog').exists()).toBe(true)
    expect(apiFetch).toHaveBeenCalledTimes(1) // só o /api/auth/me da carga inicial
  })

  it('não exclui quando o usuário volta', async () => {
    const wrapper = await mountPage()
    await requestDeletion(wrapper)

    await wrapper.find('.dialog-cancel').trigger('click')

    expect(wrapper.find('.dialog').exists()).toBe(false)
    expect(apiFetch).toHaveBeenCalledTimes(1)
  })

  it('exclui a conta, limpa a sessão e volta ao login', async () => {
    const wrapper = await mountPage()
    await requestDeletion(wrapper)
    apiFetch.mockResolvedValueOnce(null)

    await wrapper.find('.dialog-confirm').trigger('click')
    await flushPromises()

    expect(apiFetch).toHaveBeenLastCalledWith('/api/usuarios/me/exclusao', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ password: 'senha-123' }),
    }))
    expect(clearSession).toHaveBeenCalled()
    expect(push).toHaveBeenCalledWith({ name: 'Login' })
  })

  it('fecha o dialog e mostra o erro quando a senha está errada', async () => {
    const wrapper = await mountPage()
    await requestDeletion(wrapper)
    apiFetch.mockRejectedValueOnce(new Error('Senha incorreta.'))

    await wrapper.find('.dialog-confirm').trigger('click')
    await flushPromises()

    expect(wrapper.find('.dialog').exists()).toBe(false)
    expect(wrapper.find('.danger-zone .form-error').text()).toBe('Senha incorreta.')
    expect(clearSession).not.toHaveBeenCalled()
  })
})
