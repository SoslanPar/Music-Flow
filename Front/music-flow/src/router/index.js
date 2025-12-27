// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import { getCookie } from '../utils/cookies.js'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/yandex-callback',
    name: 'YandexCallback',
    component: () => import('@/components/YandexCallback.vue')
  },
  {
    path: '/main',
    name: 'Main',
    component: () => import('../views/Main.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Навигационный guard для проверки авторизации
router.beforeEach((to, from, next) => {
  const userId = getCookie('user_id')
  const isAuthenticated = !!userId
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Требуется авторизация, но пользователь не авторизован
    next({ name: 'Login' })
  } else if (to.name === 'Login' && isAuthenticated) {
    // Уже авторизован, редирект на главную
    next({ name: 'Main' })
  } else {
    next()
  }
})

export default router
