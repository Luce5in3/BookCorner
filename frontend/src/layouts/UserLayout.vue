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
  <div class="min-h-screen flex flex-col bg-apple-gray">
    <!-- Header - Apple Glass Navigation -->
    <header class="sticky top-0 z-50 bg-[rgba(0,0,0,0.8)] backdrop-blur-[20px] backdrop-saturate-[180%]">
      <div class="max-w-[980px] mx-auto px-4 sm:px-6 h-[52px] flex items-center justify-between">
        <!-- Logo -->
        <div 
          class="flex items-center gap-2.5 cursor-pointer"
          @click="router.push('/reader/home')"
        >
          <el-icon size="20" color="#FFFFFF"><Reading /></el-icon>
          <span class="text-[16px] font-semibold text-white tracking-[-0.224px]">图书角</span>
        </div>
        
        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-8">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="text-[16px] font-normal text-white/80 hover:text-white transition-opacity duration-200 tracking-[-0.224px]"
            :class="{ 'text-white font-medium underline underline-offset-4 decoration-white': activeIndex === item.path }"
          >
            {{ item.title }}
          </router-link>
        </nav>
        
        <!-- User Menu -->
        <div class="flex items-center gap-3">
          <el-dropdown trigger="click">
            <div class="flex items-center gap-2 cursor-pointer py-2">
              <div class="w-7 h-7 bg-dark-surface-3 rounded-full flex items-center justify-center">
                <el-icon size="14" color="#FFFFFF"><UserFilled /></el-icon>
              </div>
              <span class="text-[15px] text-white/80 hidden sm:block tracking-[-0.224px]">{{ username }}</span>
              <el-icon size="12" color="rgba(255,255,255,0.48)"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="!rounded-standard !border-[rgba(0,0,0,0.04)]">
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
    <nav class="md:hidden bg-apple-gray border-b border-[rgba(0,0,0,0.04)]">
      <div class="flex overflow-x-auto scrollbar-hide">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex-shrink-0 px-5 py-3 text-[15px] text-text-secondary hover:text-text-primary transition-colors whitespace-nowrap tracking-[-0.224px]"
          :class="{ '!text-near-black font-semibold': activeIndex === item.path }"
        >
          {{ item.title }}
        </router-link>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="flex-1">
      <div class="max-w-[1300px] mx-auto px-4 sm:px-6 py-8">
        <router-view />
      </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-apple-gray border-t border-[rgba(0,0,0,0.04)] py-4">
      <div class="max-w-[980px] mx-auto px-4 sm:px-6 text-center">
        <p class="text-micro">图书角图书管理系统</p>
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
  color: #ffffff;
}

/* Dropdown menu styling - Apple */
:deep(.el-dropdown-menu) {
  border-radius: 8px !important;
  border: none !important;
  box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0px !important;
  padding: 4px !important;
}

:deep(.el-dropdown-menu__item) {
  border-radius: 5px !important;
  padding: 8px 12px !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  color: #1d1d1f !important;
  letter-spacing: -0.224px !important;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f5f5f7 !important;
}
</style>
