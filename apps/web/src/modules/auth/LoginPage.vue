<template>
  <main class="login-page">
    <section class="login-intro" aria-labelledby="brand-title">
      <a class="brand" href="/" aria-label="Talentix, página inicial">
        <span class="brand-mark">T</span>
        <span>talentix</span>
      </a>

      <div class="intro-content">
        <p class="eyebrow">Recrutamento mais claro</p>
        <h1 id="brand-title">Encontre o talento certo, com mais confiança.</h1>
        <p>Uma forma simples e transparente de analisar currículos e acompanhar processos seletivos.</p>
      </div>

      <p class="intro-footer">© {{ new Date().getFullYear() }} Talentix</p>
    </section>

    <section class="login-panel" aria-labelledby="login-title">
      <div class="login-card">
        <header>
          <h2 id="login-title">Boas-vindas!</h2>
          <p>Entre com seus dados para acessar sua conta.</p>
        </header>

        <form @submit.prevent="login" novalidate>
          <label for="email">E-mail</label>
          <input id="email" v-model.trim="email" type="email" autocomplete="email" placeholder="seu@email.com" required />

          <div class="label-row">
            <label for="password">Senha</label>
            <a href="#" @click.prevent>Esqueci minha senha</a>
          </div>
          <div class="password-input">
            <input id="password" v-model="password" :type="passwordVisible ? 'text' : 'password'" autocomplete="current-password" placeholder="Digite sua senha" minlength="8" required />
            <button type="button" class="show-password" :aria-label="passwordVisible ? 'Ocultar senha' : 'Mostrar senha'" @click="passwordVisible = !passwordVisible">
              {{ passwordVisible ? 'Ocultar' : 'Mostrar' }}
            </button>
          </div>

          <p v-if="error" class="form-error" role="alert">{{ error }}</p>

          <button class="submit-button" type="submit" :disabled="loading">
            {{ loading ? 'Entrando...' : 'Entrar' }}
          </button>
        </form>

        <p class="signup">Ainda não possui uma conta? <a href="#" @click.prevent>Crie sua conta</a></p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const passwordVisible = ref(false)

async function login() {
  error.value = ''
  loading.value = true

  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Não foi possível entrar. Verifique os seus dados.')
    }

    localStorage.setItem('talentix_token', data.access_token)
    localStorage.setItem('talentix_user', JSON.stringify(data.user))
    window.dispatchEvent(new CustomEvent('talentix:login', { detail: data.user }))
  } catch (requestError) {
    error.value = requestError.message || 'Ocorreu um erro inesperado. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>
