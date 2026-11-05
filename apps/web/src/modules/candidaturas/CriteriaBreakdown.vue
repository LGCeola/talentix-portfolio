<template>
  <div class="breakdown">
    <ul class="criteria-results">
      <li v-for="criterion in criteria" :key="criterion.name">
        <div class="criterion-line">
          <strong>{{ criterion.name }}</strong>
          <span class="criterion-status" :class="criterion.status">{{ CRITERION_STATUS_LABELS[criterion.status] }}</span>
          <span class="points">{{ criterion.points }} de {{ criterion.weight }} pontos</span>
        </div>
        <p v-if="describeDetection(criterion)" class="detection">{{ describeDetection(criterion) }}</p>
        <p v-if="criterion.evidence" class="evidence">“{{ criterion.evidence }}”</p>
      </li>
    </ul>

    <div v-if="suggestions.length" class="suggestions">
      <strong>Sugestões de melhoria</strong>
      <ul>
        <li v-for="suggestion in suggestions" :key="suggestion">{{ suggestion }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { CRITERION_STATUS_LABELS, describeDetection } from './application.js'

defineProps({
  criteria: { type: Array, required: true },
  suggestions: { type: Array, default: () => [] },
})
</script>

<style scoped>
.breakdown {
  display: grid;
  gap: 12px;
  font-size: .84rem;
}

.criteria-results,
.suggestions ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.criterion-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.criterion-status {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: .72rem;
  font-weight: 700;
}

.criterion-status.present {
  background: #dcfce7;
  color: #166534;
}

.criterion-status.absent {
  background: #f1f5f9;
  color: #475569;
}

.criterion-status.review {
  background: #fef9c3;
  color: #854d0e;
}

.points {
  margin-left: auto;
  color: #64748b;
}

.detection {
  margin: 4px 0 0;
  color: #475569;
  font-size: .78rem;
}

.evidence {
  margin: 4px 0 0;
  color: #64748b;
  font-style: italic;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.suggestions {
  display: grid;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #eff6ff;
  color: #1e3a8a;
  line-height: 1.4;
}
</style>
