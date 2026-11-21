// Mantém as abas do mesmo navegador com o mesmo login.
// O login fica no localStorage, compartilhado entre as abas; quando ele muda numa aba, o navegador avisa as
// outras com o evento "storage". Sem isso, uma aba poderia mostrar um usuário enquanto age com o login de outro.
export const TOKEN_KEY = 'talentix_token'

export function watchSessionChanges({ toLogin, reload }, target = window) {
  function onStorage(event) {
    // key null: o localStorage inteiro foi limpo (por exemplo, pelas ferramentas do navegador).
    if (event.key !== TOKEN_KEY && event.key !== null) return
    if (event.key === TOKEN_KEY && event.oldValue === event.newValue) return

    if (localStorage.getItem(TOKEN_KEY)) {
      // Entrou (ou trocou de usuário) em outra aba: recarrega já com o login novo.
      reload()
    } else {
      // Saiu em outra aba: esta também volta para o login.
      toLogin()
    }
  }

  target.addEventListener('storage', onStorage)
  return () => target.removeEventListener('storage', onStorage)
}
