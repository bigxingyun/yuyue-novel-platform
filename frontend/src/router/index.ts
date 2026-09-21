import { createRouter, createWebHistory } from 'vue-router'
import { setupGuards } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('@/views/landing/LandingView.vue'),
    },
    {
      path: '/auth',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        { path: 'login', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
        { path: 'register', name: 'register', component: () => import('@/views/auth/RegisterView.vue') },
        { path: 'recover', name: 'recover', component: () => import('@/views/auth/RecoverView.vue') },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: 'square', name: 'square', component: () => import('@/views/square/SquareView.vue') },
        { path: 'book/:bookId', name: 'book', component: () => import('@/views/book/BookDetailView.vue') },
        { path: 'shelf', name: 'shelf', component: () => import('@/views/shelf/ShelfView.vue') },
        { path: 'profile', name: 'profile', component: () => import('@/views/profile/ProfileView.vue') },
        { path: 'profile/edit', name: 'profile-edit', component: () => import('@/views/profile/EditProfileView.vue') },
        { path: 'profile/password', name: 'profile-password', component: () => import('@/views/profile/ChangePasswordView.vue') },
        { path: 'profile/exp', name: 'profile-exp', component: () => import('@/views/profile/ExpLogView.vue') },
        { path: 'profile/titles', name: 'profile-titles', component: () => import('@/views/profile/TitleGuideView.vue') },
        { path: 'profile/history', name: 'profile-history', component: () => import('@/views/profile/HistoryView.vue') },
        { path: 'profile/apply-author', name: 'profile-apply-author', component: () => import('@/views/profile/AuthorApplyView.vue'), meta: { role: 'user' } },
        { path: 'profile/works', name: 'profile-works', component: () => import('@/views/profile/WorksManageView.vue'), meta: { role: 'author' } },
        { path: 'profile/works/:bookId/chapters', name: 'profile-chapters', component: () => import('@/views/profile/ChapterManageView.vue'), meta: { role: 'author' } },
      ],
    },
    {
      path: '/read/:bookId/:chapterId',
      name: 'reader',
      component: () => import('@/views/reader/ReaderView.vue'),
      meta: { requiresAuth: true, layout: 'reader' },
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        { path: '', redirect: { name: 'admin-applications' } },
        { path: 'users', name: 'admin-users', component: () => import('@/views/admin/UserManageView.vue') },
        { path: 'keys', name: 'admin-keys', component: () => import('@/views/admin/KeyManageView.vue') },
        { path: 'books', name: 'admin-books', component: () => import('@/views/admin/BookManageView.vue') },
        { path: 'books/:bookId/chapters', name: 'admin-chapters', component: () => import('@/views/admin/AdminChapterManageView.vue') },
        { path: 'applications', name: 'admin-applications', component: () => import('@/views/admin/ApplicationReviewView.vue') },
        { path: 'comments', name: 'admin-comments', component: () => import('@/views/admin/CommentManageView.vue') },
      ],
    },
  ],
})

setupGuards(router)
export default router
