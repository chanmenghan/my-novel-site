import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/novel',
      name: 'novel',
      component: () => import('../views/novel.vue'),
      children: [
        {
          path: 'inspiration',
          name: 'inspiration',
          component: () => import('../views/inspiration.vue'),
        },
        {
          path: 'continuation',
          name: 'continuation',
          component: () => import('../views/continuation.vue'),
        },
        {
          path: 'setting',
          name: 'setting',
          component: () => import('../views/setting.vue'),
        },
      ],
    },
    {
      path: '/shelf',
      name: 'shelf',
      component: () => import('../views/shelf.vue'),
    },
    {
      path: '/shelf/:id',
      name: 'book',
      component: () => import('../views/book.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/user',
      name: 'user',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router