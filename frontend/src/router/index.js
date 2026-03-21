// 路由配置
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册', guest: true }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/auth/Forbidden.vue'),
    meta: { title: '无权限' }
  },
  
  // 读者端路由
  {
    path: '/reader',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true, role: 0 },
    children: [
      {
        path: '',
        redirect: '/reader/home'
      },
      {
        path: 'home',
        name: 'ReaderHome',
        component: () => import('@/views/reader/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'book/:id',
        name: 'BookDetail',
        component: () => import('@/views/reader/BookDetail.vue'),
        meta: { title: '图书详情' }
      },
      {
        path: 'borrows',
        name: 'MyBorrows',
        component: () => import('@/views/reader/MyBorrows.vue'),
        meta: { title: '我的借阅' }
      },
      {
        path: 'reservations',
        name: 'MyReservations',
        component: () => import('@/views/reader/MyReservations.vue'),
        meta: { title: '我的预约' }
      },
      {
        path: 'fines',
        name: 'MyFines',
        component: () => import('@/views/reader/MyFines.vue'),
        meta: { title: '我的罚款' }
      }
    ]
  },
  
  // 管理员端路由
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 1 },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据总览' }
      },
      {
        path: 'books',
        name: 'BookManage',
        component: () => import('@/views/admin/BookManage.vue'),
        meta: { title: '图书管理' }
      },
      {
        path: 'copies',
        name: 'CopyManage',
        component: () => import('@/views/admin/CopyManage.vue'),
        meta: { title: '副本管理' }
      },
      {
        path: 'borrows',
        name: 'BorrowManage',
        component: () => import('@/views/admin/BorrowManage.vue'),
        meta: { title: '借阅管理' }
      },
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/admin/UserManage.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'fines',
        name: 'FineManage',
        component: () => import('@/views/admin/FineManage.vue'),
        meta: { title: '罚款管理' }
      },
      {
        path: 'announcements',
        name: 'Announcements',
        component: () => import('@/views/admin/Announcements.vue'),
        meta: { title: '公告管理' }
      }
    ]
  },
  
  // 根路径重定向
  {
    path: '/',
    redirect: '/login'
  },
  
  // 404
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 图书角` : '图书角'
  
  // 如果已登录但没有用户信息，先获取用户信息
  if (authStore.isLoggedIn && !authStore.userInfo) {
    try {
      await authStore.fetchUserInfo()
    } catch (error) {
      // 获取失败，清除登录状态
      authStore.logout()
      return next('/login')
    }
  }
  
  // 访问需要登录的页面
  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      return next('/login')
    }
    
    // 角色检查
    const requiredRole = to.meta.role
    const userRole = authStore.userRole
    
    // 管理员可以访问读者页面
    if (requiredRole !== undefined && userRole < requiredRole) {
      return next('/403')
    }
  }
  
  // 已登录用户访问登录/注册页面
  if (to.meta.guest && authStore.isLoggedIn) {
    // 根据角色跳转到对应首页
    if (authStore.isAdmin) {
      return next('/admin/dashboard')
    } else {
      return next('/reader/home')
    }
  }
  
  next()
})

export default router
