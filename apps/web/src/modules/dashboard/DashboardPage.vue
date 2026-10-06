<template>
  <div class="dashboard-placeholder">
    <p>🚧 Dashboard em construção</p>
    <button @click="logout">Sair</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  localStorage.removeItem('talentix_token')
  localStorage.removeItem('talentix_user')
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.dashboard-placeholder {
  min-height: 100vh;
  display: grid;
  place-items: center;
  gap: 16px;
  font-family: Inter, sans-serif;
  background: #f8fafc;
  color: #172033;
}
button {
  padding: 10px 24px;
  border: 0;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
</style>
