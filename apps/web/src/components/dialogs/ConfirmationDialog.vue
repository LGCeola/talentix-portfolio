<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    width="min(420px, 92vw)"
    align-center
    :show-close="!loading"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    :before-close="cancel"
  >
    <!-- O slot permite uma mensagem com formatação; sem ele, usa a prop "message". -->
    <slot>
      <p class="confirmation-message">{{ message }}</p>
    </slot>

    <template #footer>
      <el-button :disabled="loading" @click="cancel">{{ cancelText }}</el-button>
      <el-button :type="danger ? 'danger' : 'primary'" :loading="loading" @click="emit('confirm')">
        {{ confirmText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
const props = defineProps({
  // Controla se o dialog está aberto (use com v-model).
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar ação' },
  message: { type: String, default: 'Tem certeza de que deseja continuar?' },
  confirmText: { type: String, default: 'Confirmar' },
  cancelText: { type: String, default: 'Cancelar' },
  // Botão de confirmar em vermelho, para ações destrutivas (excluir, desistir).
  danger: { type: Boolean, default: false },
  // Enquanto a ação roda, o botão mostra carregamento e o dialog não pode ser fechado.
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

// Chamado pelo botão Cancelar, pelo X, pelo Esc e pelo clique fora.
function cancel() {
  if (props.loading) return
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<style scoped>
/* Mesmo estilo para a mensagem padrão e para parágrafos passados pelo slot. */
.confirmation-message,
:slotted(p) {
  margin: 0;
  color: #475569;
  line-height: 1.5;
}
</style>
