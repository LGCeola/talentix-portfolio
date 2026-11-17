import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../router/index.js', () => ({ default: { push: vi.fn() } }))

const { default: router } = await import('../router/index.js')
const { apiDownload, apiFetch, clearSession, getCurrentUser, saveCurrentUser } = await import('./api.js')

function respond(status, body, ok = status < 400) {
  return {
    status,
    ok,
    json: () => (body === undefined ? Promise.reject(new Error('sem corpo')) : Promise.resolve(body)),
    blob: () => Promise.resolve(new Blob(['conteúdo'])),
  }
}

beforeEach(() => {
  localStorage.clear()
  router.push.mockClear()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('sessão no navegador', () => {
  it('guarda, lê e limpa o usuário', () => {
    saveCurrentUser({ name: 'Ana' })
    localStorage.setItem('talentix_token', 'abc')
    expect(getCurrentUser()).toEqual({ name: 'Ana' })
    clearSession()
    expect(getCurrentUser()).toBeNull()
    expect(localStorage.getItem('talentix_token')).toBeNull()
  })

  it('não quebra com dados corrompidos', () => {
    localStorage.setItem('talentix_user', '{inválido')
    expect(getCurrentUser()).toBeNull()
  })
})

describe('apiFetch', () => {
  it('envia o token e devolve o JSON', async () => {
    localStorage.setItem('talentix_token', 'abc')
    const fetch = vi.fn().mockResolvedValue(respond(200, { id: 1 }))
    vi.stubGlobal('fetch', fetch)

    await expect(apiFetch('/api/vagas', { headers: { 'X-Teste': '1' } })).resolves.toEqual({ id: 1 })
    expect(fetch).toHaveBeenCalledWith('/api/vagas', { headers: { 'X-Teste': '1', Authorization: 'Bearer abc' } })
  })

  it('não envia token quando não há login', async () => {
    const fetch = vi.fn().mockResolvedValue(respond(200, []))
    vi.stubGlobal('fetch', fetch)
    await apiFetch('/api/vagas')
    expect(fetch.mock.calls[0][1].headers).toEqual({})
  })

  it('devolve null em respostas sem conteúdo', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(204)))
    await expect(apiFetch('/api/candidaturas/1', { method: 'DELETE' })).resolves.toBeNull()
  })

  it('usa a mensagem de erro da API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(409, { detail: 'Você já se candidatou a esta vaga' })))
    await expect(apiFetch('/api/candidaturas')).rejects.toThrow('Você já se candidatou a esta vaga')
  })

  it('traduz o primeiro erro de validação', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(422, { detail: [{ msg: 'Value error, A soma dos pesos não pode passar de 100%' }] })))
    await expect(apiFetch('/api/vagas')).rejects.toThrow('A soma dos pesos não pode passar de 100%')
  })

  it('usa uma mensagem padrão quando a API não explica o erro', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(500)))
    await expect(apiFetch('/api/vagas')).rejects.toThrow('Ocorreu um erro inesperado. Tente novamente.')
  })

  it('encerra a sessão e volta ao login quando o token expira', async () => {
    localStorage.setItem('talentix_token', 'expirado')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(401, { detail: 'x' })))

    await expect(apiFetch('/api/vagas')).rejects.toThrow('Sua sessão expirou')
    expect(localStorage.getItem('talentix_token')).toBeNull()
    expect(router.push).toHaveBeenCalledWith({ name: 'Login' })
  })
})

describe('apiDownload', () => {
  it('baixa o arquivo com o nome original', async () => {
    localStorage.setItem('talentix_token', 'abc')
    const fetch = vi.fn().mockResolvedValue(respond(200))
    vi.stubGlobal('fetch', fetch)
    URL.createObjectURL = vi.fn(() => 'blob:teste')
    URL.revokeObjectURL = vi.fn()
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    await apiDownload('/api/candidaturas/1/curriculo', 'curriculo.pdf')

    expect(fetch).toHaveBeenCalledWith('/api/candidaturas/1/curriculo', { headers: { Authorization: 'Bearer abc' } })
    expect(click).toHaveBeenCalledOnce()
    expect(click.mock.contexts[0].download).toBe('curriculo.pdf')
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:teste')
  })

  it('mostra o erro da API', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(404, { detail: 'Candidatura não encontrada' })))
    await expect(apiDownload('/api/candidaturas/9/curriculo', 'x.pdf')).rejects.toThrow('Candidatura não encontrada')
  })

  it('volta ao login quando o token expira', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respond(401, {})))
    await expect(apiDownload('/api/candidaturas/1/curriculo', 'x.pdf')).rejects.toThrow('Sua sessão expirou')
    expect(router.push).toHaveBeenCalledWith({ name: 'Login' })
  })
})
