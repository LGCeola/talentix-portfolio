import { beforeEach, describe, expect, it } from 'vitest'
import router from './index.js'

function login(userType) {
  localStorage.setItem('talentix_token', 'abc')
  localStorage.setItem('talentix_user', JSON.stringify({ user_type: userType }))
}

async function go(path) {
  await router.push(path)
  return router.currentRoute.value.name
}

beforeEach(async () => {
  localStorage.clear()
  await router.push('/login')
})

describe('proteção das rotas', () => {
  it('manda quem não está logado para o login', async () => {
    expect(await go('/dashboard')).toBe('Login')
    expect(await go('/vagas/nova')).toBe('Login')
  })

  it('manda quem já está logado para o dashboard', async () => {
    login('candidate')
    // O teste começa em /login: navegar para a mesma rota não passa pela proteção.
    expect(await go('/register')).toBe('Dashboard')
    expect(await go('/login')).toBe('Dashboard')
  })

  it('libera as telas do recrutador só para recrutadores', async () => {
    login('candidate')
    expect(await go('/vagas/nova')).toBe('Dashboard')
    expect(await go('/vagas/1/candidaturas')).toBe('Dashboard')

    login('recruiter')
    expect(await go('/vagas/nova')).toBe('VacancyCreate')
    expect(await go('/vagas/1/candidaturas')).toBe('VacancyApplications')
  })

  it('mostra "Entrar" no título só nas telas de login e cadastro', async () => {
    expect(document.title).toBe('Talentix | Entrar')
    await go('/register')
    expect(document.title).toBe('Talentix | Criar conta')

    login('candidate')
    await go('/dashboard')
    expect(document.title).toBe('Talentix')
  })

  it('trata dados de usuário corrompidos como sem permissão', async () => {
    localStorage.setItem('talentix_token', 'abc')
    localStorage.setItem('talentix_user', '{inválido')
    expect(await go('/vagas/nova')).toBe('Dashboard')
  })
})
