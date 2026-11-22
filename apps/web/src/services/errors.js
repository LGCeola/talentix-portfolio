// Transforma a resposta de erro da API em uma mensagem legível.
// O FastAPI devolve "detail" como texto (erros de regra) ou como lista (erros de validação, 422).
export function errorMessage(data, fallback) {
  if (typeof data?.detail === 'string') return data.detail
  if (Array.isArray(data?.detail)) return data.detail[0]?.msg?.replace(/^Value error, /, '') || fallback
  return fallback
}
