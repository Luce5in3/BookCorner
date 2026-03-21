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
  <el-container class="h-full" direction="vertical">
    <!-- 顶部导航 -->
    <el-header class="header-container">
      <div class="header-content">
        <div class="logo" @click="router.push('/reader/home')">
          <el-icon size="28" color="#409EFF"><Reading /></el-icon>
          <span class="logo-text">图书角</span>
        </div>
        
        <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          :ellipsis="false"
          @select="router.push"
        >
          <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">
            {{ item.title }}
          </el-menu-item>
        </el-menu>
        
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="authStore.isAdmin" @click="router.push('/admin/dashboard')">
                  <el-icon><Setting /></el-icon>管理后台
                </el-dropdown-item>
                <el-dropdown-item :divided="authStore.isAdmin" @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <!-- 主内容区 -->
    <el-main class="main-container">
      <div class="content-wrapper">
        <router-view />
      </div>
    </el-main>
    
    <!-- 底部 -->
    <el-footer class="footer-container">
      <p>图书角图书管理系统 © 2024</p>
    </el-footer>
  </el-container>
</template>

<style scoped>
.header-container {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 40px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.el-menu {
  flex: 1;
  border-bottom: none;
}

.el-menu--horizontal > .el-menu-item {
  height: 60px;
  line-height: 60px;
}

.header-right {
  margin-left: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}

.username {
  font-size: 14px;
}

.main-container {
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-container {
  background: #fff;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  border-top: 1px solid #eee;
}
</style>
