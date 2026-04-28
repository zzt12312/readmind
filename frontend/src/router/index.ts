import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { routes } from '@/constants/routes'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: routes.dashboard,
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
        },
        {
          path: 'import',
          name: 'import',
          component: () => import('@/views/import/ImportCenterView.vue'),
        },
        {
          path: 'books',
          name: 'books',
          component: () => import('@/views/books/BookLibraryView.vue'),
        },
        {
          path: 'books/:id',
          name: 'book-detail',
          component: () => import('@/views/books/BookDetailView.vue'),
        },
        {
          path: 'notes',
          name: 'notes',
          component: () => import('@/views/notes/NoteWorkbenchView.vue'),
        },
        {
          path: 'graph',
          name: 'graph',
          component: () => import('@/views/graph/TopicGraphView.vue'),
        },
        {
          path: 'jobs',
          name: 'jobs',
          component: () => import('@/views/jobs/JobsCenterView.vue'),
        },
        {
          path: 'qa',
          name: 'qa',
          component: () => import('@/views/qa/QaCenterView.vue'),
        },
        {
          path: 'review',
          name: 'review',
          component: () => import('@/views/review/ReviewCenterView.vue'),
        },
      ],
    },
    {
      path: '/login',
      component: AuthLayout,
      children: [
        {
          path: '',
          name: 'login',
          component: () => import('@/views/auth/LoginView.vue'),
        },
      ],
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
