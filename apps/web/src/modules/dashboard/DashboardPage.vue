<template>
  <AppLayout>
    <CandidateDashboard v-if="user?.user_type === 'candidate'" />
    <RecruiterDashboard v-else />
  </AppLayout>
</template>

<script setup>
import AppLayout from '../../components/AppLayout.vue'
import CandidateDashboard from './CandidateDashboard.vue'
import RecruiterDashboard from './RecruiterDashboard.vue'
import { getCurrentUser } from '../../services/api.js'

const user = getCurrentUser()
</script>
