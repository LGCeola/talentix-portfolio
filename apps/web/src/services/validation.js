// Formato básico de e-mail: algo@dominio.ext, sem espaços.
// A validação completa continua no backend (Pydantic EmailStr); aqui é só para dar uma mensagem em português.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isValidEmail(email) {
  return EMAIL_PATTERN.test(email)
}
