// Formato básico de e-mail: algo@dominio.ext, sem espaços.
// A validação completa continua no backend (Pydantic EmailStr); aqui é só para dar uma mensagem em português.
// Feito sem expressão regular para não haver risco de backtracking lento (regra javascript:S8786 do Sonar).
export function isValidEmail(email) {
  if (/\s/.test(email)) return false

  const at = email.indexOf('@')
  if (at < 1 || at !== email.lastIndexOf('@')) return false

  const domain = email.slice(at + 1)
  const dot = domain.lastIndexOf('.')
  return dot > 0 && dot < domain.length - 1
}
