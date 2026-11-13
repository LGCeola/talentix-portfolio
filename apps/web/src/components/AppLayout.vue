<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/dashboard" aria-label="Talentix, dashboard">
        <span class="brand-mark">T</span>
        <span>talentix</span>
      </RouterLink>

      <ProfileDropdown :user-name="userName" />
    </header>

    <main class="app-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import ProfileDropdown from '../modules/auth/components/dropdown/ProfileDropdown.vue'

defineProps({
  // Permite à página de conta mostrar o nome recém-editado.
  userName: { type: String, default: null },
})
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

.app-content {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px clamp(16px, 4vw, 40px);
}
</style>
