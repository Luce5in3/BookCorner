<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

async function handleLogin() {
  try {
    await formRef.value.validate()
    loading.value = true
    
    await authStore.login(form)
    
    ElMessage.success('登录成功')
    
    // 根据角色跳转
    if (authStore.isAdmin) {
      router.push('/admin/dashboard')
    } else {
      router.push('/reader/home')
    }
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-nike-white">
    <div class="w-full max-w-[440px] px-6">
      <!-- Logo Section -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-nike-black rounded-full mb-6">
          <el-icon size="32" color="#FFFFFF"><Reading /></el-icon>
        </div>
        <h1 class="text-h1 font-medium text-text-primary mb-2">图书角</h1>
        <p class="text-body text-text-secondary">图书管理系统</p>
      </div>
      
      <!-- Login Form -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="space-y-5"
      >
        <el-form-item prop="username" class="!mb-0">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            class="nike-input"
          >
            <template #prefix>
              <el-icon class="text-text-secondary"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password" class="!mb-0">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            class="nike-input"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="text-text-secondary"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item class="!mb-0 pt-2">
          <button
            type="button"
            :disabled="loading"
            class="w-full h-12 bg-nike-black text-nike-white font-medium text-button rounded-pill border-none cursor-pointer transition-all duration-200 hover:bg-text-secondary disabled:bg-text-disabled disabled:cursor-not-allowed"
            @click="handleLogin"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <el-icon class="animate-spin"><Loading /></el-icon>
              登录中...
            </span>
            <span v-else>登录</span>
          </button>
        </el-form-item>
      </el-form>
      
      <!-- Footer -->
      <div class="mt-8 text-center">
        <span class="text-link-sm text-text-secondary">还没有账号？</span>
        <button 
          type="button"
          class="ml-1 text-link-sm font-medium text-text-primary underline underline-offset-4 hover:text-text-secondary transition-colors"
          @click="router.push('/register')"
        >
          立即注册
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Nike Style Input Overrides */
:deep(.nike-input .el-input__wrapper) {
  background-color: #F5F5F5 !important;
  border-radius: 8px !important;
  box-shadow: none !important;
  padding: 0 16px !important;
  height: 52px !important;
}

:deep(.nike-input .el-input__inner) {
  color: #111111 !important;
  font-size: 16px !important;
  font-weight: 400 !important;
}

:deep(.nike-input .el-input__inner::placeholder) {
  color: #707072 !important;
}

:deep(.nike-input .el-input__prefix) {
  margin-right: 12px !important;
}

/* Remove default form item margin */
:deep(.el-form-item) {
  margin-bottom: 0 !important;
}

:deep(.el-form-item__error) {
  color: #D30005 !important;
  font-size: 12px !important;
  padding-top: 4px !important;
}
</style>
