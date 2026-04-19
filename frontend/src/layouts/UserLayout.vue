<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = computed(() => authStore.userInfo?.real_name || authStore.userInfo?.username || '用户')

const navItems = [
  { path: '/reader/home', title: '首页' },
  { path: '/reader/borrows', title: '我的借阅' },
  { path: '/reader/reservations', title: '我的预约' },
  { path: '/reader/fines', title: '我的罚款' }
]

const activeIndex = computed(() => {
  const path = route.path
  if (path.startsWith('/reader/book/')) return '/reader/home'
  return path
})

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    authStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-light-gray">
    <!-- Header - Nike Style Sticky Nav -->
    <header class="sticky top-0 z-50 bg-nike-white border-b border-border-secondary">
      <div class="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-12 h-[60px] flex items-center justify-between">
        <!-- Logo -->
        <div 
          class="flex items-center gap-2 cursor-pointer"
          @click="router.push('/reader/home')"
        >
          <div class="w-8 h-8 bg-nike-black rounded-full flex items-center justify-center">
            <el-icon size="18" color="#FFFFFF"><Reading /></el-icon>
          </div>
          <span class="text-h3 font-medium text-text-primary">图书角</span>
        </div>
        
        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-8">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="text-link font-medium text-text-primary hover:text-text-secondary transition-colors duration-200 py-5 border-b-2 border-transparent"
            :class="{ 'border-nike-black !text-text-primary': activeIndex === item.path }"
          >
            {{ item.title }}
          </router-link>
        </nav>
        
        <!-- User Menu -->
        <div class="flex items-center gap-4">
          <el-dropdown trigger="click">
            <div class="flex items-center gap-2 cursor-pointer py-2">
              <div class="w-8 h-8 bg-light-gray rounded-full flex items-center justify-center">
                <el-icon size="16" class="text-text-secondary"><UserFilled /></el-icon>
              </div>
              <span class="text-body-medium text-text-primary hidden sm:block">{{ username }}</span>
              <el-icon class="text-text-secondary"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="!rounded-card !border-border-secondary">
                <el-dropdown-item v-if="authStore.isAdmin" @click="router.push('/admin/dashboard')">
                  <el-icon class="mr-2"><Setting /></el-icon>管理后台
                </el-dropdown-item>
                <el-dropdown-item :divided="authStore.isAdmin" @click="handleLogout">
                  <el-icon class="mr-2"><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>
    
    <!-- Mobile Navigation -->
    <nav class="md:hidden bg-nike-white border-b border-border-secondary">
      <div class="flex overflow-x-auto scrollbar-hide">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex-shrink-0 px-5 py-3 text-link-sm font-medium text-text-primary hover:text-text-secondary transition-colors whitespace-nowrap"
          :class="{ 'text-text-primary border-b-2 border-nike-black': activeIndex === item.path }"
        >
          {{ item.title }}
        </router-link>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="flex-1">
      <div class="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-12 py-6">
        <router-view />
      </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-nike-white border-t border-border-secondary py-5">
      <div class="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-12 text-center">
        <p class="text-small text-text-secondary">图书角图书管理系统 &copy; 2024</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Hide scrollbar for mobile nav */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Router link active state */
.router-link-active {
  color: #111111;
}

/* Dropdown menu styling */
:deep(.el-dropdown-menu) {
  border-radius: 20px !important;
  border: 1px solid #CACACB !important;
  box-shadow: none !important;
  padding: 8px !important;
}

:deep(.el-dropdown-menu__item) {
  border-radius: 12px !important;
  padding: 10px 16px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: #111111 !important;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #F5F5F5 !important;
}
</style>
