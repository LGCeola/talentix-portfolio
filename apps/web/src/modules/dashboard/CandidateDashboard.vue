<template>
  <div class="candidate-grid">
    <section class="panel" aria-labelledby="resume-title">
      <h2 id="resume-title">Meu currículo</h2>

      <div class="score-ring" aria-label="Nota do currículo">
        <strong>—</strong>
        <span>/ 100</span>
      </div>
      <p class="score-caption">
        {{ resumes.length ? 'Análise pendente — a nota aparecerá aqui assim que o algoritmo for executado.' : 'Envie seu currículo para receber uma nota.' }}
      </p>

      <label
        class="dropzone"
        :class="{ dragging, disabled: uploading }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
      >
        <input type="file" accept=".pdf,.txt,application/pdf,text/plain" :disabled="uploading" @change="onSelect" />
        <UploadIcon class="dropzone-icon" />
        <strong>{{ uploading ? 'Enviando...' : 'Clique ou arraste seu currículo' }}</strong>
        <span>PDF ou TXT, até {{ MAX_SIZE_MB }} MB</span>
      </label>

      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <p v-if="success" class="form-success" role="status">{{ success }}</p>

      <ul v-if="resumes.length" class="resume-list">
        <li v-for="resume in resumes" :key="resume.id">
          <FileTextIcon class="resume-icon" />
          <div class="resume-info">
            <strong>{{ resume.original_filename }}</strong>
            <span>Enviado em {{ formatDate(resume.updated_at) }}</span>
          </div>
          <span class="badge">Análise pendente</span>
          <button
            type="button"
            class="icon-button"
            :aria-label="`Excluir ${resume.original_filename}`"
            :disabled="deletingId === resume.id"
            @click="removeResume(resume)"
          >
            <TrashIcon />
          </button>
        </li>
      </ul>
      <p v-else-if="!loading" class="empty">Nenhum currículo enviado ainda.</p>
    </section>

    <CandidateVacancies :resumes="resumes" />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import UploadIcon from '~icons/lucide/upload'
import FileTextIcon from '~icons/lucide/file-text'
import TrashIcon from '~icons/lucide/trash-2'
import { apiFetch } from '../../services/api.js'
import CandidateVacancies from '../candidaturas/CandidateVacancies.vue'

const MAX_SIZE_MB = 5
const ALLOWED_EXTENSIONS = ['pdf', 'txt']

const resumes = ref([])
const loading = ref(true)
const uploading = ref(false)
const deletingId = ref(null)
const dragging = ref(false)
const error = ref('')
const success = ref('')

onMounted(loadResumes)

async function loadResumes() {
  loading.value = true
  try {
    resumes.value = await apiFetch('/api/curriculos')
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

function onSelect(event) {
  const [file] = event.target.files
  event.target.value = ''
  if (file) upload(file)
}

function onDrop(event) {
  dragging.value = false
  const [file] = event.dataTransfer.files
  if (file && !uploading.value) upload(file)
}

async function upload(file) {
  error.value = ''
  success.value = ''

  const extension = file.name.split('.').pop().toLowerCase()
  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    error.value = 'Formato não suportado. Envie um arquivo PDF ou TXT.'
    return
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    error.value = `O arquivo excede o limite de ${MAX_SIZE_MB} MB.`
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  uploading.value = true
  try {
    const resume = await apiFetch('/api/curriculos', { method: 'POST', body: formData })
    resumes.value.unshift(resume)
    success.value = 'Currículo enviado com sucesso!'
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    uploading.value = false
  }
}

async function removeResume(resume) {
  error.value = ''
  success.value = ''
  deletingId.value = resume.id
  try {
    await apiFetch(`/api/curriculos/${resume.id}`, { method: 'DELETE' })
    resumes.value = resumes.value.filter((item) => item.id !== resume.id)
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    deletingId.value = null
  }
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.candidate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr));
  gap: 24px;
  align-items: start;
}

h2 {
  margin: 0 0 20px;
  font-size: 1.15rem;
}

.score-ring {
  width: 132px;
  height: 132px;
  margin: 0 auto;
  display: flex;
  align-items: baseline;
  justify-content: center;
  padding-top: 44px;
  gap: 4px;
  border: 8px solid #e2e8f0;
  border-radius: 50%;
}

.score-ring strong {
  font-size: 1.8rem;
  color: #94a3b8;
}

.score-ring span {
  color: #94a3b8;
}

.score-caption {
  margin: 12px auto 24px;
  max-width: 320px;
  text-align: center;
  color: #64748b;
  font-size: .88rem;
  line-height: 1.45;
}

.dropzone {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 4px;
  padding: 24px 16px;
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: border-color .15s, background .15s;
}

.dropzone:hover,
.dropzone.dragging {
  border-color: #2563eb;
  background: #eff6ff;
}

.dropzone.disabled {
  cursor: progress;
  opacity: .6;
}

.dropzone input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
}

.dropzone:focus-within {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

.dropzone-icon {
  width: 28px;
  height: 28px;
  color: #2563eb;
}

.dropzone span {
  color: #64748b;
  font-size: .85rem;
}

.form-error,
.form-success {
  margin: 16px 0 0;
}

.resume-list {
  margin: 20px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 10px;
}

.resume-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.resume-icon {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  color: #475569;
}

.resume-info {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 2px;
}

.resume-info strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resume-info span {
  color: #64748b;
  font-size: .8rem;
}

.badge {
  flex-shrink: 0;
  padding: 4px 8px;
  border-radius: 999px;
  background: #fef9c3;
  color: #854d0e;
  font-size: .75rem;
  font-weight: 600;
}

.icon-button {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.icon-button:hover:not(:disabled) {
  background: #fef3f2;
  color: #b42318;
}

.icon-button:disabled {
  cursor: progress;
  opacity: .5;
}

.empty {
  margin: 16px 0 0;
  color: #64748b;
  font-size: .9rem;
}

@media (max-width: 480px) {
  .badge {
    display: none;
  }
}
</style>
