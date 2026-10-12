<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/dashboard" aria-label="Talentix, dashboard">
        <span class="brand-mark">T</span>
        <span>talentix</span>
      </RouterLink>

      <div class="topbar-user">
        <span>{{ user?.name }}</span>
        <button type="button" class="logout-button" @click="logout">Sair</button>
      </div>
    </header>

    <main class="app-content">
      <CandidateDashboard v-if="user?.user_type === 'candidate'" />
      <section v-else class="panel placeholder">
        <h2>Dashboard do recrutador</h2>
        <p>A criação de vagas e o ranking de candidatos chegam no próximo marco.</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import CandidateDashboard from './CandidateDashboard.vue'
import { clearSession, getCurrentUser } from '../../services/api.js'

const router = useRouter()
const user = getCurrentUser()

function logout() {
  clearSession()
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f8fafc;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px clamp(16px, 4vw, 40px);
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.topbar .brand {
  color: #172033;
}

.topbar .brand-mark {
  border-color: #2563eb;
  background: #2563eb;
  color: #fff;
}

.topbar-user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #475569;
  font-weight: 600;
}

.logout-button {
  padding: 8px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: #172033;
  font-weight: 600;
  cursor: pointer;
}

.logout-button:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.app-content {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px clamp(16px, 4vw, 40px);
}

.placeholder h2 {
  margin: 0 0 8px;
}

.placeholder p {
  margin: 0;
  color: #64748b;
}
</style>
