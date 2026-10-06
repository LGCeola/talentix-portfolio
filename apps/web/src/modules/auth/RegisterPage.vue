<template>
  <main class="auth-page">
    <!-- Painel esquerdo: branding -->
    <section class="auth-intro" aria-labelledby="brand-title">
      <RouterLink class="brand" to="/" aria-label="Talentix, página inicial">
        <span class="brand-mark">T</span>
        <span>talentix</span>
      </RouterLink>

      <div class="intro-content">
        <p class="eyebrow">Sua carreira começa aqui</p>
        <h1 id="brand-title">Junte-se à plataforma que torna o recrutamento transparente.</h1>
        <p>Análise inteligente de currículos com critérios claros. Sem caixas-pretas, sem mistério.</p>
      </div>

      <p class="intro-footer">© {{ new Date().getFullYear() }} Talentix</p>
    </section>

    <!-- Painel direito: formulário -->
    <section class="auth-panel" aria-labelledby="register-title">
      <div class="auth-card">

        <!-- Step 1: Seleção de tipo -->
        <Transition name="step" mode="out-in">
          <div v-if="step === 1" key="type-selection">
            <header>
              <h2 id="register-title">Criar conta</h2>
              <p>Escolha como você vai usar o Talentix.</p>
            </header>

            <div class="type-cards">
              <button
                class="type-card"
                :class="{ active: selectedType === 'candidate' }"
                type="button"
                @click="selectedType = 'candidate'"
              >
                <span class="type-icon">🎯</span>
                <strong>Candidato</strong>
                <span>Envie seu currículo e descubra seus pontos fortes.</span>
              </button>

              <button
                class="type-card"
                :class="{ active: selectedType === 'recruiter' }"
                type="button"
                @click="selectedType = 'recruiter'"
              >
                <span class="type-icon">🏢</span>
                <strong>Recrutador</strong>
                <span>Crie vagas e encontre os melhores candidatos.</span>
              </button>
            </div>

            <button
              class="submit-button"
              type="button"
              :disabled="!selectedType"
              @click="step = 2"
            >
              Continuar
              <span class="btn-arrow">→</span>
            </button>

            <p class="login-link">
              Já tem uma conta?
              <RouterLink to="/login">Entrar</RouterLink>
            </p>
          </div>

          <!-- Step 2: Dados do usuário -->
          <div v-else key="user-form">
            <header>
              <button class="back-btn" type="button" @click="step = 1" aria-label="Voltar">
                ← Voltar
              </button>
              <h2 id="register-title">
                {{ selectedType === 'candidate' ? 'Dados do candidato' : 'Dados do recrutador' }}
              </h2>
              <p>Preencha suas informações para criar a conta.</p>
            </header>

            <form @submit.prevent="register" novalidate>
              <label for="name">Nome completo</label>
              <input
                id="name"
                v-model.trim="name"
                type="text"
                autocomplete="name"
                placeholder="Seu nome"
                required
              />

              <label for="email">E-mail</label>
              <input
                id="email"
                v-model.trim="email"
                type="email"
                autocomplete="email"
                placeholder="seu@email.com"
                required
              />

              <label for="password">Senha</label>
              <div class="password-input">
                <input
                  id="password"
                  v-model="password"
                  :type="passwordVisible ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="Mínimo 8 caracteres"
                  minlength="8"
                  required
                />
                <button
                  type="button"
                  class="show-password"
                  :aria-label="passwordVisible ? 'Ocultar senha' : 'Mostrar senha'"
                  @click="passwordVisible = !passwordVisible"
                >
                  <EyeOffIcon v-if="passwordVisible" />
                  <EyeIcon v-else />
                </button>
              </div>

              <div class="password-strength" v-if="password">
                <div class="strength-bar">
                  <span
                    v-for="n in 4"
                    :key="n"
                    class="strength-segment"
                    :class="{ filled: passwordStrength >= n, [`level-${passwordStrength}`]: passwordStrength >= n }"
                  />
                </div>
                <span class="strength-label">{{ strengthLabel }}</span>
              </div>

              <p v-if="error" class="form-error" role="alert">{{ error }}</p>

              <button class="submit-button" type="submit" :disabled="loading">
                {{ loading ? 'Criando conta...' : 'Criar conta' }}
              </button>
            </form>

            <p class="login-link">
              Já tem uma conta?
              <RouterLink to="/login">Entrar</RouterLink>
            </p>
          </div>
        </Transition>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import EyeIcon from '~icons/lucide/eye'
import EyeOffIcon from '~icons/lucide/eye-off'

const router = useRouter()

const step = ref(1)
const selectedType = ref('')
const name = ref('')
const email = ref('')
const password = ref('')
const passwordVisible = ref(false)
const loading = ref(false)
const error = ref('')

const passwordStrength = computed(() => {
  const p = password.value
  if (!p) return 0
  let score = 0
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthLabel = computed(() => {
  return ['', 'Fraca', 'Razoável', 'Boa', 'Forte'][passwordStrength.value] ?? ''
})

async function register() {
  error.value = ''

  if (password.value.length < 8) {
    error.value = 'A senha deve ter no mínimo 8 caracteres.'
    return
  }

  loading.value = true

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value,
        email: email.value,
        password: password.value,
        user_type: selectedType.value,
      }),
    })

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Não foi possível criar a conta.')
    }

    router.push({ name: 'Login', query: { registered: '1' } })
  } catch (requestError) {
    error.value = requestError.message || 'Ocorreu um erro inesperado. Tente novamente.'
  } finally {
    loading.value = false
  }
}
</script>
