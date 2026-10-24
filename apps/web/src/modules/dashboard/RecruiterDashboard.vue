<template>
  <div class="recruiter-dashboard">
    <section class="stats" aria-label="Resumo">
      <article class="panel stat">
        <h2>Candidatos recebidos</h2>
        <strong>{{ loading ? '—' : totalApplications }}</strong>
      </article>
      <article class="panel stat">
        <h2>Média de pontuações</h2>
        <strong>—</strong>
        <span>Disponível após a análise dos currículos</span>
      </article>
      <article class="panel stat">
        <h2>Vagas ativas</h2>
        <strong>{{ loading ? '—' : openCount }}</strong>
      </article>
    </section>

    <section class="panel" aria-labelledby="vacancies-title">
      <header class="section-header">
        <h2 id="vacancies-title">Minhas vagas</h2>
        <RouterLink class="primary-link" :to="{ name: 'VacancyCreate' }">
          <PlusIcon /> Nova vaga
        </RouterLink>
      </header>

      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <ul v-if="vacancies.length" class="vacancy-list">
        <li v-for="vacancy in vacancies" :key="vacancy.id">
          <div class="vacancy-info">
            <strong>{{ vacancy.title }}</strong>
            <span>
              {{ vacancy.criteria_count }} {{ vacancy.criteria_count === 1 ? 'critério' : 'critérios' }}
              · {{ vacancy.applications_count }} {{ vacancy.applications_count === 1 ? 'candidato' : 'candidatos' }}
              · criada em {{ formatDate(vacancy.created_at) }}
            </span>
          </div>

          <span class="status-badge" :class="vacancy.status">{{ STATUS_LABELS[vacancy.status] }}</span>

          <div class="actions">
            <RouterLink
              v-if="vacancy.status !== 'draft'"
              class="action"
              :to="{ name: 'VacancyApplications', params: { id: vacancy.id } }"
            >Candidatos</RouterLink>
            <RouterLink
              v-if="vacancy.status !== 'closed' && vacancy.applications_count === 0"
              class="action"
              :to="{ name: 'VacancyEdit', params: { id: vacancy.id } }"
            >Editar</RouterLink>
            <button v-if="vacancy.status === 'draft'" type="button" class="action" :disabled="busyId === vacancy.id" @click="changeStatus(vacancy, 'open')">Publicar</button>
            <button v-if="vacancy.status === 'open'" type="button" class="action" :disabled="busyId === vacancy.id" @click="changeStatus(vacancy, 'closed')">Encerrar</button>
            <button v-if="vacancy.status === 'closed'" type="button" class="action" :disabled="busyId === vacancy.id" @click="changeStatus(vacancy, 'open')">Reabrir</button>
            <button v-if="vacancy.status === 'draft'" type="button" class="action danger" :disabled="busyId === vacancy.id" @click="remove(vacancy)">Excluir</button>
          </div>
        </li>
      </ul>
      <p v-else-if="!loading" class="empty">Você ainda não criou nenhuma vaga.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PlusIcon from '~icons/lucide/plus'
import { apiFetch } from '../../services/api.js'
import { STATUS_LABELS } from '../vagas/vacancy.js'

const vacancies = ref([])
const loading = ref(true)
const busyId = ref(null)
const error = ref('')

const openCount = computed(() => vacancies.value.filter((vacancy) => vacancy.status === 'open').length)
const totalApplications = computed(() => vacancies.value.reduce((sum, vacancy) => sum + vacancy.applications_count, 0))

onMounted(loadVacancies)

async function loadVacancies() {
  loading.value = true
  try {
    vacancies.value = await apiFetch('/api/vagas/minhas')
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

async function changeStatus(vacancy, status) {
  error.value = ''
  busyId.value = vacancy.id
  try {
    const updated = await apiFetch(`/api/vagas/${vacancy.id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    vacancy.status = updated.status
  } catch (requestError) {
    error.value = `"${vacancy.title}": ${requestError.message}`
  } finally {
    busyId.value = null
  }
}

async function remove(vacancy) {
  if (!window.confirm(`Excluir o rascunho "${vacancy.title}"?`)) return
  error.value = ''
  busyId.value = vacancy.id
  try {
    await apiFetch(`/api/vagas/${vacancy.id}`, { method: 'DELETE' })
    vacancies.value = vacancies.value.filter((item) => item.id !== vacancy.id)
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    busyId.value = null
  }
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.recruiter-dashboard {
  display: grid;
  gap: 24px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr));
  gap: 24px;
}

.stat {
  display: grid;
  justify-items: center;
  gap: 8px;
  text-align: center;
}

.stat h2 {
  margin: 0;
  font-size: .95rem;
  color: #475569;
}

.stat strong {
  font-size: 2.6rem;
  color: #2563eb;
  line-height: 1.1;
}

.stat span {
  color: #94a3b8;
  font-size: .8rem;
}

.section-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.15rem;
}

.primary-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 700;
  text-decoration: none;
}

.primary-link:hover {
  background: #1d4ed8;
}

.form-error {
  margin: 0 0 16px;
}

.vacancy-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

.vacancy-list li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.vacancy-info {
  flex: 1 1 240px;
  min-width: 0;
  display: grid;
  gap: 2px;
}

.vacancy-info span {
  color: #64748b;
  font-size: .82rem;
}


.actions {
  display: flex;
  gap: 6px;
}

.action {
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  background: #fff;
  color: #172033;
  font-size: .85rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}

.action:hover:not(:disabled) {
  border-color: #2563eb;
  color: #2563eb;
}

.action.danger:hover:not(:disabled) {
  border-color: #b42318;
  color: #b42318;
}

.action:disabled {
  cursor: progress;
  opacity: .5;
}

.empty {
  margin: 0;
  color: #64748b;
  font-size: .9rem;
}
</style>
