import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../modules/auth/LoginPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../modules/auth/RegisterPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../modules/dashboard/DashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/vagas/nova',
    name: 'VacancyCreate',
    component: () => import('../modules/vagas/VacancyFormPage.vue'),
    meta: { requiresAuth: true, role: 'recruiter' },
  },
  {
    path: '/vagas/:id(\\d+)/editar',
    name: 'VacancyEdit',
    component: () => import('../modules/vagas/VacancyFormPage.vue'),
    meta: { requiresAuth: true, role: 'recruiter' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('talentix_token')
  const isAuthenticated = !!token

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'Login' }
  }

  if (to.meta.guest && isAuthenticated) {
    return { name: 'Dashboard' }
  }

  if (to.meta.role) {
    let user = null
    try {
      user = JSON.parse(localStorage.getItem('talentix_user'))
    } catch {}
    if (user?.user_type !== to.meta.role) {
      return { name: 'Dashboard' }
    }
  }
})

export default router
