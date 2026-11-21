import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { TOKEN_KEY, watchSessionChanges } from './sessionSync.js'

// Simula outra aba alterando o login: o navegador grava no localStorage e avisa esta aba com "storage".
function otherTabChanges(key, oldValue, newValue) {
  if (key === null) localStorage.clear()
  else if (newValue === null) localStorage.removeItem(key)
  else localStorage.setItem(key, newValue)
  window.dispatchEvent(new StorageEvent('storage', { key, oldValue, newValue }))
}

let actions
let stop

beforeEach(() => {
  localStorage.clear()
  localStorage.setItem(TOKEN_KEY, 'token-usuario-a')
  actions = { toLogin: vi.fn(), reload: vi.fn() }
  stop = watchSessionChanges(actions)
})

afterEach(() => {
  stop()
  localStorage.clear()
})

describe('watchSessionChanges', () => {
  it('leva esta aba ao login quando outra aba sai', () => {
    otherTabChanges(TOKEN_KEY, 'token-usuario-a', null)
    expect(actions.toLogin).toHaveBeenCalledOnce()
    expect(actions.reload).not.toHaveBeenCalled()
  })

  it('recarrega esta aba quando outra entra com outro usuário', () => {
    otherTabChanges(TOKEN_KEY, 'token-usuario-a', 'token-usuario-b')
    expect(actions.reload).toHaveBeenCalledOnce()
    expect(actions.toLogin).not.toHaveBeenCalled()
  })

  it('recarrega a tela de login quando outra aba entra', () => {
    localStorage.removeItem(TOKEN_KEY)
    otherTabChanges(TOKEN_KEY, null, 'token-usuario-a')
    expect(actions.reload).toHaveBeenCalledOnce()
  })

  it('trata a limpeza total do armazenamento como saída', () => {
    otherTabChanges(null, null, null)
    expect(actions.toLogin).toHaveBeenCalledOnce()
  })

  it('ignora outras chaves e eventos sem mudança no login', () => {
    otherTabChanges('talentix_user', '{"name":"A"}', '{"name":"A editado"}')
    otherTabChanges(TOKEN_KEY, 'token-usuario-a', 'token-usuario-a')
    expect(actions.toLogin).not.toHaveBeenCalled()
    expect(actions.reload).not.toHaveBeenCalled()
  })

  it('para de escutar quando desligado', () => {
    stop()
    otherTabChanges(TOKEN_KEY, 'token-usuario-a', null)
    expect(actions.toLogin).not.toHaveBeenCalled()
  })
})
