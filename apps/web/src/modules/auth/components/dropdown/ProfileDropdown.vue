<template>
    <el-dropdown trigger="click" placement="bottom-end" @command="handleCommand">
        <button type="button" class="user-menu-trigger">
            <span>{{ userName ?? user?.name }}</span>
            <ChevronDownIcon aria-hidden="true" />
        </button>

        <template #dropdown>
            <el-dropdown-menu>
                <el-dropdown-item command="profile">
                    <UserIcon class="menu-icon" aria-hidden="true" />
                    Perfil
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                    <LogOutIcon class="menu-icon" aria-hidden="true" />
                    Sair
                </el-dropdown-item>
            </el-dropdown-menu>
        </template>
    </el-dropdown>

    <!-- Fora do dropdown: o menu fecha ao clicar em "Sair", e o dialog precisa continuar aberto. -->
    <ConfirmationDialog
        v-model="logoutDialogOpen"
        title="Sair"
        confirm-text="Sair"
        cancel-text="Voltar"
        danger
        @confirm="logout"
    >
        <p>Deseja mesmo encerrar a sessão? <br> Você precisará entrar novamente para acessar sua conta.</p>
    </ConfirmationDialog>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ChevronDownIcon from '~icons/lucide/chevron-down'
import LogOutIcon from '~icons/lucide/log-out'
import UserIcon from '~icons/lucide/user'
import { clearSession, getCurrentUser } from '../../../../services/api.js'
import ConfirmationDialog from '../../../../components/dialogs/ConfirmationDialog.vue'

defineProps({
    // Quando informado, substitui o nome salvo na sessão (ex.: logo após editar a conta).
    userName: { type: String, default: null },
})

const router = useRouter()
const user = getCurrentUser()
const logoutDialogOpen = ref(false)

function logout() {
    logoutDialogOpen.value = false
    clearSession()
    router.push({ name: 'Login' })
}

function handleCommand(command) {
    if (command === 'profile') router.push({ name: 'Account' })
    // "Sair" só abre a confirmação; quem encerra a sessão é o @confirm do dialog.
    if (command === 'logout') logoutDialogOpen.value = true
}
</script>

<style scoped>
.user-menu-trigger {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border: 1px solid transparent;
    border-radius: 8px;
    background: transparent;
    color: #475569;
    font: inherit;
    font-weight: 600;
    cursor: pointer;
}

.user-menu-trigger:hover,
.user-menu-trigger:focus-visible {
    border-color: #cbd5e1;
    color: #2563eb;
}

.menu-icon {
    margin-right: 8px;
}
</style>
