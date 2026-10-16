<template>
  <AppLayout>
    <section class="panel form-panel" aria-labelledby="vacancy-form-title">
      <header class="form-header">
        <h1 id="vacancy-form-title">{{ isEdit ? 'Editar vaga' : 'Nova vaga' }}</h1>
        <span v-if="isEdit && currentStatus" class="status-badge" :class="currentStatus">{{ STATUS_LABELS[currentStatus] }}</span>
      </header>

      <p v-if="loading" class="hint">Carregando vaga...</p>

      <form v-else novalidate @submit.prevent>
        <label for="title">Título da vaga</label>
        <input id="title" v-model="title" type="text" maxlength="100" placeholder="Ex.: Desenvolvedor Python Júnior" />

        <label for="description">Descrição</label>
        <textarea id="description" v-model="description" rows="6" maxlength="10000" placeholder="Responsabilidades, contexto da equipe, regime de trabalho..."></textarea>

        <fieldset class="criteria">
          <legend>Requisitos e pesos</legend>
          <p class="hint">
            Cada requisito vale uma parte da nota final do candidato, de 0 a 100. Para publicar, os pesos precisam somar 100%.
          </p>

          <div v-for="(criterion, index) in criteria" :key="criterion.key" class="criterion-row">
            <input
              v-model="criterion.name"
              type="text"
              maxlength="50"
              :aria-label="`Nome do requisito ${index + 1}`"
              placeholder="Ex.: Python, Graduação em TI"
            />
            <select v-model="criterion.criterion_type" :aria-label="`Tipo do requisito ${index + 1}`">
              <option v-for="type in CRITERION_TYPES" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
            <div class="weight-input">
              <input
                v-model.number="criterion.weight"
                type="number"
                min="1"
                max="100"
                :aria-label="`Peso do requisito ${index + 1} em porcentagem`"
              />
              <span>%</span>
            </div>
            <button type="button" class="icon-button" :aria-label="`Remover requisito ${index + 1}`" @click="removeCriterion(index)">
              <TrashIcon />
            </button>
          </div>

          <button type="button" class="add-button" :disabled="criteria.length >= 30" @click="addCriterion">
            <PlusIcon /> Adicionar requisito
          </button>

          <div class="total" :class="totalState">
            <div class="total-bar"><span :style="{ width: `${Math.min(total, 100)}%` }"></span></div>
            <strong>Total: {{ total }}% de 100%</strong>
          </div>
        </fieldset>

        <p v-if="error" class="form-error" role="alert">{{ error }}</p>

        <div class="form-actions">
          <RouterLink class="secondary-button" :to="{ name: 'Dashboard' }">Voltar</RouterLink>
          <template v-if="currentStatus !== 'closed'">
            <button v-if="currentStatus !== 'open'" type="button" class="secondary-button" :disabled="saving || !canSaveDraft" @click="save('draft')">
              Salvar rascunho
            </button>
            <button type="button" class="primary-button" :disabled="saving || !canPublish" @click="save('open')">
              {{ currentStatus === 'open' ? 'Salvar alterações' : 'Postar' }}
            </button>
          </template>
        </div>
        <p v-if="publishBlocker && currentStatus !== 'closed'" class="hint blocker">{{ publishBlocker }}</p>
      </form>
    </section>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PlusIcon from '~icons/lucide/plus'
import TrashIcon from '~icons/lucide/trash-2'
import AppLayout from '../../components/AppLayout.vue'
import { apiFetch } from '../../services/api.js'
import { CRITERION_TYPES, STATUS_LABELS, totalWeight } from './vacancy.js'

const route = useRoute()
const router = useRouter()

const vacancyId = route.params.id
const isEdit = Boolean(vacancyId)

const title = ref('')
const description = ref('')
const criteria = ref([])
const currentStatus = ref(null)
const loading = ref(isEdit)
const saving = ref(false)
const error = ref('')

let nextKey = 0
function newCriterion(data = {}) {
  return { key: nextKey++, name: '', criterion_type: 'habilidade', weight: 10, ...data }
}

const total = computed(() => totalWeight(criteria.value))
const totalState = computed(() => (total.value === 100 ? 'complete' : total.value > 100 ? 'over' : 'under'))

const criteriaValid = computed(() =>
  criteria.value.every((criterion) =>
    criterion.name.trim().length >= 2 && Number.isInteger(criterion.weight) && criterion.weight >= 1 && criterion.weight <= 100
  )
)
const canSaveDraft = computed(() => title.value.trim().length >= 3 && criteriaValid.value && total.value <= 100)

const publishBlocker = computed(() => {
  if (title.value.trim().length < 3) return 'Informe um título com pelo menos 3 caracteres.'
  if (!description.value.trim()) return 'Informe a descrição da vaga para publicá-la.'
  if (!criteria.value.length) return 'Adicione pelo menos um requisito.'
  if (!criteriaValid.value) return 'Cada requisito precisa de um nome (mín. 2 caracteres) e um peso inteiro entre 1 e 100.'
  if (total.value !== 100) return `Os pesos somam ${total.value}%; ajuste para exatamente 100% para publicar.`
  return ''
})
const canPublish = computed(() => !publishBlocker.value)

onMounted(async () => {
  if (!isEdit) {
    criteria.value = [newCriterion()]
    return
  }
  try {
    const vacancy = await apiFetch(`/api/vagas/${vacancyId}`)
    title.value = vacancy.title
    description.value = vacancy.description
    criteria.value = vacancy.criteria.map(({ name, criterion_type, weight }) => newCriterion({ name, criterion_type, weight }))
    currentStatus.value = vacancy.status
    if (vacancy.status === 'closed') error.value = 'Vagas encerradas não podem ser editadas.'
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
})

function addCriterion() {
  criteria.value.push(newCriterion({ weight: Math.max(1, Math.min(100 - total.value, 100)) }))
}

function removeCriterion(index) {
  criteria.value.splice(index, 1)
}

async function save(status) {
  error.value = ''
  saving.value = true
  try {
    await apiFetch(isEdit ? `/api/vagas/${vacancyId}` : '/api/vagas', {
      method: isEdit ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title.value,
        description: description.value,
        status,
        criteria: criteria.value.map(({ name, criterion_type, weight }) => ({ name, criterion_type, weight })),
      }),
    })
    router.push({ name: 'Dashboard' })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-panel {
  max-width: 760px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.form-header h1 {
  margin: 0;
  font-size: 1.4rem;
}

textarea,
select {
  width: 100%;
  padding: 13px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
  color: #172033;
  background: #fff;
  font: inherit;
  transition: border-color .15s, box-shadow .15s;
}

textarea {
  resize: vertical;
}

textarea:focus,
select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px #dbeafe;
}

.criteria {
  margin: 12px 0 0;
  padding: 0;
  border: 0;
  display: grid;
  gap: 10px;
}

.criteria legend {
  padding: 0;
  font-size: .9rem;
  font-weight: 650;
  color: #334155;
}

.hint {
  margin: 0;
  color: #64748b;
  font-size: .85rem;
  line-height: 1.45;
}

.criterion-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px 100px 40px;
  gap: 8px;
  align-items: center;
}

.weight-input {
  position: relative;
}

.weight-input input {
  padding-right: 28px;
}

.weight-input span {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
}

.icon-button {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.icon-button:hover {
  background: #fef3f2;
  color: #b42318;
}

.add-button {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px dashed #93c5fd;
  border-radius: 8px;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
  cursor: pointer;
}

.add-button:disabled {
  cursor: not-allowed;
  opacity: .5;
}

.total {
  display: grid;
  gap: 6px;
  margin-top: 4px;
}

.total-bar {
  height: 8px;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.total-bar span {
  display: block;
  height: 100%;
  background: currentColor;
  transition: width .2s;
}

.total strong {
  font-size: .9rem;
}

.total.under {
  color: #b45309;
}

.total.complete {
  color: #15803d;
}

.total.over {
  color: #b42318;
}

.form-error {
  margin: 12px 0 0;
}

.form-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.primary-button,
.secondary-button {
  min-height: 44px;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  cursor: pointer;
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

.secondary-button:hover:not(:disabled) {
  border-color: #2563eb;
  color: #2563eb;
}

.primary-button:disabled,
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: .55;
}

.blocker {
  text-align: right;
}


@media (max-width: 600px) {
  .criterion-row {
    grid-template-columns: minmax(0, 1fr) 90px 40px;
  }

  .criterion-row input[type="text"] {
    grid-column: 1 / -1;
  }

  .blocker {
    text-align: left;
  }
}
</style>
