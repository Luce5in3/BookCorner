<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isCollapse = ref(false)

const username = computed(() => authStore.userInfo?.real_name || authStore.userInfo?.username || '管理员')

const menuItems = [
  { index: '/admin/dashboard', icon: 'DataAnalysis', title: '数据总览' },
  { index: '/admin/books', icon: 'Reading', title: '图书管理' },
  { index: '/admin/copies', icon: 'Files', title: '副本管理' },
  { index: '/admin/borrows', icon: 'Tickets', title: '借阅管理' },
  { index: '/admin/users', icon: 'User', title: '用户管理' },
  { index: '/admin/fines', icon: 'Money', title: '罚款管理' },
  { index: '/admin/announcements', icon: 'Bell', title: '公告管理' }
]

const activeMenu = computed(() => route.path)

function handleMenuSelect(index) {
  router.push(index)
}

function toggleCollapse() {
  isCollapse.value = !isCollapse.value
}

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
  <div class="min-h-screen flex bg-light-gray">
    <!-- Sidebar - Nike Dark Theme -->
    <aside 
      class="fixed left-0 top-0 h-screen bg-nike-black transition-all duration-300 z-50 flex flex-col"
      :class="isCollapse ? 'w-16' : 'w-56'"
    >
      <!-- Logo -->
      <div class="h-[60px] flex items-center justify-center gap-2 border-b border-grey-700">
        <div class="w-8 h-8 bg-nike-white rounded-full flex items-center justify-center flex-shrink-0">
          <el-icon size="18" color="#111111"><Reading /></el-icon>
        </div>
        <span 
          v-if="!isCollapse" 
          class="text-h3 font-medium text-nike-white whitespace-nowrap"
        >
          图书角管理
        </span>
      </div>
      
      <!-- Menu -->
      <nav class="flex-1 py-4 overflow-y-auto">
        <ul class="space-y-1 px-2">
          <li v-for="item in menuItems" :key="item.index">
            <button
              class="w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 text-left"
              :class="activeMenu === item.index 
                ? 'bg-grey-700 text-nike-white' 
                : 'text-grey-400 hover:bg-grey-700 hover:text-nike-white'"
              @click="handleMenuSelect(item.index)"
            >
              <el-icon size="18" class="flex-shrink-0">
                <component :is="item.icon" />
              </el-icon>
              <span 
                v-if="!isCollapse" 
                class="text-link-sm font-medium whitespace-nowrap"
              >
                {{ item.title }}
              </span>
            </button>
          </li>
        </ul>
      </nav>
      
      <!-- Collapse Button -->
      <div class="p-3 border-t border-grey-700">
        <button
          class="w-full flex items-center justify-center p-2 rounded-lg text-grey-400 hover:bg-grey-700 hover:text-nike-white transition-all duration-200"
          @click="toggleCollapse"
        >
          <el-icon size="18">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </button>
      </div>
    </aside>
    
    <!-- Main Content Area -->
    <div 
      class="flex-1 flex flex-col min-h-screen transition-all duration-300"
      :class="isCollapse ? 'ml-16' : 'ml-56'"
    >
      <!-- Header -->
      <header class="sticky top-0 z-40 bg-nike-white border-b border-border-secondary h-[60px] flex items-center justify-between px-6">
        <!-- Breadcrumb -->
        <div class="flex items-center gap-2">
          <span class="text-link-sm text-text-secondary">管理后台</span>
          <span class="text-link-sm text-text-secondary">/</span>
          <span class="text-link-sm font-medium text-text-primary">{{ route.meta.title }}</span>
        </div>
        
        <!-- User Menu -->
        <div class="flex items-center gap-4">
          <el-dropdown trigger="click">
            <div class="flex items-center gap-2 cursor-pointer py-2">
              <div class="w-8 h-8 bg-light-gray rounded-full flex items-center justify-center">
                <el-icon size="16" class="text-text-secondary"><UserFilled /></el-icon>
              </div>
              <span class="text-body-medium text-text-primary">{{ username }}</span>
              <el-icon class="text-text-secondary"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="!rounded-card !border-border-secondary">
                <el-dropdown-item @click="router.push('/reader/home')">
                  <el-icon class="mr-2"><House /></el-icon>读者端
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon class="mr-2"><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- Main Content -->
      <main class="flex-1 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
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

/* Scrollbar for sidebar */
aside::-webkit-scrollbar {
  width: 4px;
}

aside::-webkit-scrollbar-track {
  background: transparent;
}

aside::-webkit-scrollbar-thumb {
  background: #39393B;
  border-radius: 2px;
}

aside::-webkit-scrollbar-thumb:hover {
  background: #707072;
}
</style>
