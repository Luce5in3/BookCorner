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
  <div class="min-h-screen flex bg-apple-gray">
    <!-- Sidebar - Apple Dark Theme -->
    <aside 
      class="fixed left-0 top-0 h-screen bg-near-black transition-all duration-300 z-50 flex flex-col"
      :class="isCollapse ? 'w-16' : 'w-56'"
    >
      <!-- Logo -->
      <div class="h-[48px] flex items-center justify-center gap-2 border-b border-[rgba(255,255,255,0.1)]">
        <div class="w-7 h-7 bg-apple-blue rounded-full flex items-center justify-center flex-shrink-0">
          <el-icon size="14" color="#FFFFFF"><Reading /></el-icon>
        </div>
        <span 
          v-if="!isCollapse" 
          class="text-[15px] font-semibold text-white tracking-[-0.224px]"
        >
          图书角管理
        </span>
      </div>
      
      <!-- Menu -->
      <nav class="flex-1 py-3 overflow-y-auto">
        <ul class="space-y-1 px-2">
          <li v-for="item in menuItems" :key="item.index">
            <button
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-standard transition-all duration-200 text-left"
              :class="activeMenu === item.index 
                ? 'bg-apple-blue text-white' 
                : 'text-white/70 hover:bg-[rgba(255,255,255,0.08)] hover:text-white'"
              @click="handleMenuSelect(item.index)"
            >
              <el-icon size="16" class="flex-shrink-0">
                <component :is="item.icon" />
              </el-icon>
              <span 
                v-if="!isCollapse" 
                class="text-[14px] font-normal tracking-[-0.224px] whitespace-nowrap"
              >
                {{ item.title }}
              </span>
            </button>
          </li>
        </ul>
      </nav>
      
      <!-- Collapse Button -->
      <div class="p-2.5 border-t border-[rgba(255,255,255,0.1)]">
        <button
          class="w-full flex items-center justify-center p-2 rounded-standard text-white/70 hover:bg-[rgba(255,255,255,0.08)] hover:text-white transition-all duration-200"
          @click="toggleCollapse"
        >
          <el-icon size="16">
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
      <!-- Header - Apple Glass -->
      <header class="sticky top-0 z-40 bg-[rgba(255,255,255,0.72)] backdrop-blur-[20px] backdrop-saturate-[180%] border-b border-[rgba(0,0,0,0.1)] h-[48px] flex items-center justify-end px-5">
        <!-- User Menu -->
        <div class="flex items-center gap-3">
          <el-dropdown trigger="click">
            <div class="flex items-center gap-2 cursor-pointer py-1.5">
              <div class="w-7 h-7 bg-apple-gray rounded-full flex items-center justify-center">
                <el-icon size="14" class="text-text-tertiary"><UserFilled /></el-icon>
              </div>
              <span class="text-[14px] text-text-secondary tracking-[-0.224px]">{{ username }}</span>
              <el-icon size="12" class="text-text-tertiary"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="!rounded-standard">
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
      <main class="flex-1 p-5">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
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

/* Scrollbar for sidebar */
aside::-webkit-scrollbar {
  width: 4px;
}

aside::-webkit-scrollbar-track {
  background: transparent;
}

aside::-webkit-scrollbar-thumb {
  background: #2a2a2d;
  border-radius: 2px;
}

aside::-webkit-scrollbar-thumb:hover {
  background: #3a3a3d;
}
</style>
