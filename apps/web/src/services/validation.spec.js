import { describe, expect, it } from 'vitest'
import { isValidEmail } from './validation.js'

describe('isValidEmail', () => {
  it.each(['ana@exemplo.com', 'ana.silva+vagas@empresa.com.br'])('aceita %s', (email) => {
    expect(isValidEmail(email)).toBe(true)
  })

  it.each(['', 'ana', 'ana@', 'ana@exemplo', '@exemplo.com', 'ana silva@exemplo.com', 'ana@@exemplo.com', 'ana@.com', 'ana@exemplo.'])('recusa "%s"', (email) => {
    expect(isValidEmail(email)).toBe(false)
  })
})
