<template>
  <el-dialog
    :model-value="modelValue"
    class="confirmation-dialog"
    width="min(420px, 92vw)"
    align-center
    :show-close="!loading"
    :close-on-click-modal="!loading"
    :close-on-press-escape="!loading"
    :before-close="cancel"
  >
    <!-- Cabeçalho centralizado: ícone de alerta e título. -->
    <template #header>
      <div class="confirmation-header">
        <span class="confirmation-icon" :class="danger ? 'is-danger' : 'is-primary'" aria-hidden="true">
          <CircleAlertIcon />
        </span>
        <h2 class="confirmation-title">{{ title }}</h2>
      </div>
    </template>

    <!-- O slot permite uma mensagem com formatação; sem ele, usa a prop "message". -->
    <slot>
      <p class="confirmation-message">{{ message }}</p>
    </slot>

    <template #footer>
      <div class="confirmation-actions">
        <el-button :disabled="loading" @click="cancel">{{ cancelText }}</el-button>
        <el-button :type="danger ? 'danger' : 'primary'" :loading="loading" @click="emit('confirm')">
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import CircleAlertIcon from '~icons/lucide/circle-alert'

const props = defineProps({
  // Controla se o dialog está aberto (use com v-model).
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar ação' },
  message: { type: String, default: 'Tem certeza de que deseja continuar?' },
  confirmText: { type: String, default: 'Confirmar' },
  cancelText: { type: String, default: 'Cancelar' },
  // Botão de confirmar e ícone em vermelho, para ações destrutivas (excluir, desistir).
  danger: { type: Boolean, default: false },
  // Enquanto a ação roda, o botão mostra carregamento e o dialog não pode ser fechado.
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

function cancel() {
  if (props.loading) return
  emit('update:modelValue', false)
  emit('cancel')
}
</script>

<style scoped>
.confirmation-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding-top: 8px;
}

/* Ícone com dois anéis suaves em volta, na cor da ação. */
.confirmation-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
}

.confirmation-icon svg {
  width: 24px;
  height: 24px;
}

.confirmation-icon.is-danger {
  color: var(--el-color-danger);
  background: var(--el-color-danger-light-8);
  box-shadow: 0 0 0 8px var(--el-color-danger-light-9);
}

.confirmation-icon.is-primary {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-8);
  box-shadow: 0 0 0 8px var(--el-color-primary-light-9);
}

.confirmation-title {
  margin: 4px 0 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
}

/* Mesmo estilo para a mensagem padrão e para parágrafos passados pelo slot.
   A mensagem fica alinhada à esquerda (não centralizada). */
.confirmation-message,
:slotted(p) {
  margin: 0;
  color: #475569;
  line-height: 1.5;
}

/* Botões lado a lado, com a mesma largura. */
.confirmation-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.confirmation-actions .el-button {
  height: 44px;
  margin: 0;
  border-radius: 10px;
  font-weight: 600;
}
</style>

<style>
/* O dialog é teleportado para o <body>, então o contêiner precisa de estilo global. */
.el-dialog.confirmation-dialog {
  padding: 28px;
  border-radius: 20px;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.18);
}

/* Sem o recuo à direita reservado para o X, o título fica centralizado de verdade. */
.el-dialog.confirmation-dialog .el-dialog__header {
  padding-right: 0;
  padding-bottom: 12px;
}

.el-dialog.confirmation-dialog .el-dialog__footer {
  padding-top: 24px;
}
</style>
