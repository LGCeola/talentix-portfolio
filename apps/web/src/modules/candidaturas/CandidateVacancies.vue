<template>
  <div class="candidate-vacancies">
    <section class="panel" aria-labelledby="open-vacancies-title">
      <h2 id="open-vacancies-title">Vagas abertas</h2>

      <p v-if="error" class="form-error" role="alert">{{ error }}</p>

      <ul v-if="vacancies.length" class="vacancy-cards">
        <li v-for="vacancy in vacancies" :key="vacancy.id" class="vacancy-card">
          <h3>{{ vacancy.title }}</h3>
          <p class="description">{{ vacancy.description }}</p>

          <div class="criteria" aria-label="Critérios de avaliação">
            <span class="criteria-label">Como você será avaliado:</span>
            <ul>
              <li v-for="criterion in vacancy.criteria" :key="criterion.id" :title="CRITERION_TYPE_LABELS[criterion.criterion_type]">
                {{ criterion.name }} <strong>{{ criterion.weight }}%</strong>
              </li>
            </ul>
          </div>

          <span v-if="vacancy.already_applied" class="applied-badge">✓ Candidatura enviada</span>

          <form v-else-if="applyingId === vacancy.id" class="apply-form" @submit.prevent="apply(vacancy)">
            <label :for="`resume-${vacancy.id}`">Currículo a enviar</label>
            <select :id="`resume-${vacancy.id}`" v-model="selectedResumeId" required>
              <option v-for="resume in resumes" :key="resume.id" :value="resume.id">{{ resume.original_filename }}</option>
            </select>

            <label class="consent">
              <input v-model="consent" type="checkbox" />
              <span>Autorizo o compartilhamento do meu currículo e dos meus dados de contato com o recrutador desta vaga.</span>
            </label>

            <div class="apply-actions">
              <button type="button" class="secondary-button" @click="cancelApply">Cancelar</button>
              <button type="submit" class="primary-button" :disabled="!consent || !selectedResumeId || submitting">
                {{ submitting ? 'Enviando...' : 'Confirmar candidatura' }}
              </button>
            </div>
          </form>

          <template v-else>
            <button type="button" class="primary-button" :disabled="!resumes.length" @click="startApply(vacancy)">Candidatar-se</button>
            <p v-if="!resumes.length" class="hint">Envie um currículo para se candidatar.</p>
          </template>
        </li>
      </ul>
      <p v-else-if="!loading" class="empty">Nenhuma vaga aberta no momento.</p>
    </section>

    <section class="panel" aria-labelledby="my-applications-title">
      <h2 id="my-applications-title">Minhas candidaturas</h2>

      <ul v-if="applications.length" class="application-list">
        <li v-for="application in applications" :key="application.id">
          <div class="application-info">
            <strong>{{ application.vacancy.title }}</strong>
            <span>{{ application.resume.original_filename }} · enviada em {{ formatDate(application.applied_at) }}</span>
          </div>
          <span class="score">{{ formatScore(application.overall_score) }}</span>
          <span class="application-status" :class="application.status">{{ APPLICATION_STATUS_LABELS[application.status] }}</span>
          <button
            v-if="application.status === 'pending'"
            type="button"
            class="link-button"
            :disabled="withdrawingId === application.id"
            @click="withdraw(application)"
          >Desistir</button>
        </li>
      </ul>
      <p v-else-if="!loading" class="empty">Você ainda não se candidatou a nenhuma vaga.</p>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { apiFetch } from '../../services/api.js'
import { CRITERION_TYPE_LABELS } from '../vagas/vacancy.js'
import { APPLICATION_STATUS_LABELS, formatScore } from './application.js'

const props = defineProps({
  resumes: { type: Array, required: true },
})

const vacancies = ref([])
const applications = ref([])
const loading = ref(true)
const error = ref('')

const applyingId = ref(null)
const selectedResumeId = ref(null)
const consent = ref(false)
const submitting = ref(false)
const withdrawingId = ref(null)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const [openVacancies, myApplications] = await Promise.all([
      apiFetch('/api/vagas'),
      apiFetch('/api/candidaturas/minhas'),
    ])
    vacancies.value = openVacancies
    applications.value = myApplications
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

function startApply(vacancy) {
  error.value = ''
  applyingId.value = vacancy.id
  selectedResumeId.value = props.resumes[0]?.id ?? null
  consent.value = false
}

function cancelApply() {
  applyingId.value = null
}

async function apply(vacancy) {
  error.value = ''
  submitting.value = true
  try {
    const application = await apiFetch('/api/candidaturas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vacancy_id: vacancy.id, resume_id: selectedResumeId.value, consent: consent.value }),
    })
    applications.value.unshift(application)
    vacancy.already_applied = true
    applyingId.value = null
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    submitting.value = false
  }
}

async function withdraw(application) {
  if (!window.confirm(`Desistir da candidatura para "${application.vacancy.title}"?`)) return
  error.value = ''
  withdrawingId.value = application.id
  try {
    await apiFetch(`/api/candidaturas/${application.id}`, { method: 'DELETE' })
    applications.value = applications.value.filter((item) => item.id !== application.id)
    const vacancy = vacancies.value.find((item) => item.id === application.vacancy.id)
    if (vacancy) vacancy.already_applied = false
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    withdrawingId.value = null
  }
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.candidate-vacancies {
  display: grid;
  gap: 24px;
}

h2 {
  margin: 0 0 16px;
  font-size: 1.15rem;
}

.form-error {
  margin: 0 0 16px;
}

.vacancy-cards,
.application-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 12px;
}

.vacancy-card {
  display: grid;
  gap: 10px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.vacancy-card h3 {
  margin: 0;
  font-size: 1rem;
}

.description {
  margin: 0;
  color: #475569;
  font-size: .88rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: pre-line;
}

.criteria-label {
  display: block;
  margin-bottom: 6px;
  color: #64748b;
  font-size: .78rem;
  font-weight: 600;
}

.criteria ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.criteria li {
  padding: 3px 9px;
  border-radius: 999px;
  background: #eff6ff;
  color: #1e40af;
  font-size: .78rem;
}

.applied-badge {
  justify-self: start;
  padding: 6px 12px;
  border-radius: 8px;
  background: #dcfce7;
  color: #166534;
  font-size: .85rem;
  font-weight: 600;
}

.apply-form {
  display: grid;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.apply-form select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: #172033;
  font: inherit;
}

.consent {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-weight: 400;
  font-size: .82rem;
  line-height: 1.4;
  color: #334155;
  cursor: pointer;
}

.consent input {
  width: auto;
  padding: 0;
  margin-top: 2px;
  flex-shrink: 0;
}

.apply-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.primary-button,
.secondary-button {
  min-height: 38px;
  padding: 0 16px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.vacancy-card > .primary-button {
  justify-self: start;
}

.primary-button {
  border: 0;
  background: #2563eb;
  color: #fff;
}

.primary-button:hover:not(:disabled) {
  background: #1d4ed8;
}

.secondary-button {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #172033;
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: .55;
}

.hint {
  margin: -4px 0 0;
  color: #64748b;
  font-size: .8rem;
}

.application-list li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.application-info {
  flex: 1 1 200px;
  min-width: 0;
  display: grid;
  gap: 2px;
}

.application-info span {
  color: #64748b;
  font-size: .8rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score {
  color: #64748b;
  font-size: .8rem;
}


.link-button {
  border: 0;
  background: none;
  color: #b42318;
  font-size: .85rem;
  font-weight: 600;
  cursor: pointer;
}

.link-button:disabled {
  cursor: progress;
  opacity: .5;
}

.empty {
  margin: 0;
  color: #64748b;
  font-size: .9rem;
}
</style>
