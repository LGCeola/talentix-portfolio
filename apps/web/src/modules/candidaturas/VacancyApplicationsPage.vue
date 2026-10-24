<template>
  <AppLayout>
    <div class="applications-page">
      <RouterLink class="back-link" :to="{ name: 'Dashboard' }">← Voltar ao dashboard</RouterLink>

      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <section v-if="vacancy" class="panel" aria-labelledby="vacancy-title">
        <header class="vacancy-header">
          <h1 id="vacancy-title">{{ vacancy.title }}</h1>
          <span class="status-badge" :class="vacancy.status">{{ STATUS_LABELS[vacancy.status] }}</span>
        </header>
        <ul class="criteria" aria-label="Critérios de avaliação">
          <li v-for="criterion in vacancy.criteria" :key="criterion.id">
            {{ criterion.name }} <span>({{ CRITERION_TYPE_LABELS[criterion.criterion_type] }})</span> <strong>{{ criterion.weight }}%</strong>
          </li>
        </ul>
      </section>

      <section v-if="vacancy" class="panel" aria-labelledby="candidates-title">
        <h2 id="candidates-title">Candidatos ({{ applications.length }})</h2>
        <p class="hint">
          O ranking por compatibilidade será gerado após a análise automática dos currículos.
          A decisão final é sempre do recrutador.
        </p>

        <div v-if="applications.length" class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th scope="col">Candidato</th>
                <th scope="col">Currículo</th>
                <th scope="col">Candidatura</th>
                <th scope="col">Pontuação</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="application in applications" :key="application.id">
                <td>
                  <strong>{{ application.candidate.name }}</strong>
                  <span>{{ application.candidate.email }}</span>
                </td>
                <td>{{ application.resume.original_filename }}</td>
                <td>{{ formatDate(application.applied_at) }}</td>
                <td class="muted">{{ formatScore(application.overall_score) }}</td>
                <td><span class="application-status" :class="application.status">{{ APPLICATION_STATUS_LABELS[application.status] }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty">Esta vaga ainda não recebeu candidaturas.</p>
      </section>

      <p v-else-if="loading" class="hint">Carregando...</p>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
import { apiFetch } from '../../services/api.js'
import { CRITERION_TYPE_LABELS, STATUS_LABELS } from '../vagas/vacancy.js'
import { APPLICATION_STATUS_LABELS, formatScore } from './application.js'

const route = useRoute()
const vacancy = ref(null)
const applications = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [vacancyData, applicationData] = await Promise.all([
      apiFetch(`/api/vagas/${route.params.id}`),
      apiFetch(`/api/vagas/${route.params.id}/candidaturas`),
    ])
    vacancy.value = vacancyData
    applications.value = applicationData
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
})

function formatDate(value) {
  return new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.applications-page {
  display: grid;
  gap: 20px;
}

.back-link {
  justify-self: start;
  font-weight: 600;
  text-decoration: none;
}

.vacancy-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.vacancy-header h1 {
  margin: 0;
  font-size: 1.4rem;
}

.criteria {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.criteria li {
  padding: 4px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1e40af;
  font-size: .82rem;
}

.criteria span {
  color: #64748b;
}

h2 {
  margin: 0 0 6px;
  font-size: 1.15rem;
}

.hint {
  margin: 0 0 16px;
  color: #64748b;
  font-size: .85rem;
  line-height: 1.45;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 640px;
  border-collapse: collapse;
  font-size: .9rem;
}

th {
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #64748b;
  font-size: .78rem;
  font-weight: 700;
  text-align: left;
  text-transform: uppercase;
  letter-spacing: .03em;
}

td {
  padding: 12px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

td strong,
td span:not(.application-status) {
  display: block;
}

td span:not(.application-status) {
  color: #64748b;
  font-size: .8rem;
}

.muted {
  color: #64748b;
}


.form-error {
  margin: 0;
}

.empty {
  margin: 0;
  color: #64748b;
  font-size: .9rem;
}
</style>
