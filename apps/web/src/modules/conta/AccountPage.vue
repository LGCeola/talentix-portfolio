<template>
  <AppLayout :user-name="savedName">
    <div class="account-page">
      <RouterLink class="back-link" :to="{ name: 'Dashboard' }">← Voltar ao dashboard</RouterLink>

      <section class="panel" aria-labelledby="profile-title">
        <h1 id="profile-title">Minha conta</h1>
        <p v-if="loading" class="hint">Carregando...</p>

        <form v-else novalidate @submit.prevent="saveProfile">
          <label for="name">Nome</label>
          <input id="name" v-model="name" type="text" maxlength="100" autocomplete="name" />

          <label for="email">E-mail</label>
          <input id="email" v-model.trim="email" type="email" maxlength="100" autocomplete="email" />

          <template v-if="emailChanged">
            <label for="current-password">Senha atual</label>
            <input id="current-password" v-model="currentPassword" type="password" autocomplete="current-password" />
            <p class="hint">Confirme sua senha para alterar o e-mail, que é o seu login.</p>
          </template>

          <p class="hint">Perfil: {{ user?.user_type === 'recruiter' ? 'Recrutador' : 'Candidato' }}</p>

          <p v-if="profileError" class="form-error" role="alert">{{ profileError }}</p>
          <p v-if="profileSuccess" class="form-success" role="status">{{ profileSuccess }}</p>

          <button class="submit-button" type="submit" :disabled="saving">{{ saving ? 'Salvando...' : 'Salvar alterações' }}</button>
        </form>
      </section>

      <section class="panel danger-zone" aria-labelledby="delete-title">
        <h2 id="delete-title">Excluir conta</h2>
        <p>Esta ação é definitiva e não pode ser desfeita. Serão apagados:</p>
        <ul v-if="user?.user_type === 'recruiter'">
          <li>seu cadastro;</li>
          <li>todas as suas vagas e critérios;</li>
          <li>as candidaturas recebidas nessas vagas, inclusive as já avaliadas.</li>
        </ul>
        <ul v-else>
          <li>seu cadastro;</li>
          <li>todos os seus currículos e arquivos;</li>
          <li>todas as suas candidaturas, inclusive as já avaliadas, e sua posição nos rankings.</li>
        </ul>

        <form novalidate @submit.prevent="deleteAccount">
          <label for="delete-password">Confirme sua senha</label>
          <input id="delete-password" v-model="deletePassword" type="password" autocomplete="current-password" />

          <label class="confirm-check">
            <input v-model="deleteConfirmed" type="checkbox" />
            <span>Entendo que todos esses dados serão apagados definitivamente.</span>
          </label>

          <p v-if="deleteError" class="form-error" role="alert">{{ deleteError }}</p>

          <button class="delete-button" type="submit" :disabled="deleting || !deleteConfirmed || !deletePassword">
            {{ deleting ? 'Excluindo...' : 'Excluir minha conta' }}
          </button>
        </form>
      </section>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
import { apiFetch, clearSession, getCurrentUser, saveCurrentUser } from '../../services/api.js'

const router = useRouter()

const user = ref(getCurrentUser())
const savedName = ref(user.value?.name ?? null)
const name = ref(user.value?.name ?? '')
const email = ref(user.value?.email ?? '')
const currentPassword = ref('')
const loading = ref(true)
const saving = ref(false)
const profileError = ref('')
const profileSuccess = ref('')

const deletePassword = ref('')
const deleteConfirmed = ref(false)
const deleting = ref(false)
const deleteError = ref('')

const emailChanged = computed(() => email.value.toLowerCase() !== user.value?.email)

onMounted(async () => {
  try {
    applyUser(await apiFetch('/api/auth/me'))
  } catch (requestError) {
    profileError.value = requestError.message
  } finally {
    loading.value = false
  }
})

function applyUser(data) {
  user.value = data
  savedName.value = data.name
  name.value = data.name
  email.value = data.email
  saveCurrentUser(data)
}

async function saveProfile() {
  profileError.value = ''
  profileSuccess.value = ''
  saving.value = true
  try {
    applyUser(await apiFetch('/api/usuarios/me', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.value, email: email.value, current_password: currentPassword.value || null }),
    }))
    currentPassword.value = ''
    profileSuccess.value = 'Dados atualizados.'
  } catch (requestError) {
    profileError.value = requestError.message
  } finally {
    saving.value = false
  }
}

async function deleteAccount() {
  deleteError.value = ''
  deleting.value = true
  try {
    await apiFetch('/api/usuarios/me/exclusao', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: deletePassword.value }),
    })
    clearSession()
    router.push({ name: 'Login' })
  } catch (requestError) {
    deleteError.value = requestError.message
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.account-page {
  max-width: 620px;
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.back-link {
  justify-self: start;
  font-weight: 600;
  text-decoration: none;
}

h1 {
  margin: 0 0 16px;
  font-size: 1.4rem;
}

h2 {
  margin: 0 0 8px;
  font-size: 1.15rem;
  color: #b42318;
}

.hint {
  margin: 0;
  color: #64748b;
  font-size: .85rem;
  line-height: 1.45;
}

.danger-zone {
  border-color: #fecdca;
}

.danger-zone p,
.danger-zone ul {
  margin-top: 0;
  color: #475569;
  font-size: .9rem;
  line-height: 1.5;
}

.danger-zone ul {
  padding-left: 20px;
}

.confirm-check {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 6px;
  font-weight: 400;
  font-size: .85rem;
  line-height: 1.4;
  cursor: pointer;
}

.confirm-check input {
  width: auto;
  padding: 0;
  margin-top: 2px;
  flex-shrink: 0;
}

.form-error,
.form-success {
  margin: 8px 0 0;
}

.delete-button {
  justify-self: start;
  min-height: 44px;
  margin-top: 8px;
  padding: 0 20px;
  border: 0;
  border-radius: 8px;
  background: #b42318;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.delete-button:hover:not(:disabled) {
  background: #912018;
}

.delete-button:disabled {
  cursor: not-allowed;
  opacity: .55;
}
</style>
