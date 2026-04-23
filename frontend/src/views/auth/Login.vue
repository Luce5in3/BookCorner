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
  <div class="min-h-screen flex items-center justify-center bg-apple-white">
    <div class="w-full max-w-[400px] px-6">
      <!-- Logo Section - Apple Hero Style -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-apple-black rounded-full mb-5">
          <el-icon size="28" color="#FFFFFF"><Reading /></el-icon>
        </div>
        <h1 class="text-[40px] font-semibold text-near-black leading-[1.10] mb-1">图书角</h1>
        <p class="text-[21px] font-normal text-text-secondary leading-[1.19] tracking-[0.231px]">图书管理系统</p>
      </div>
      
      <!-- Login Form -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="space-y-4"
      >
        <el-form-item prop="username" class="!mb-0">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            class="apple-input"
          >
            <template #prefix>
              <el-icon class="text-text-tertiary"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password" class="!mb-0">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            class="apple-input"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="text-text-tertiary"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <!-- Login Button -->
      <div class="mt-6">
        <button
          type="button"
          :disabled="loading"
          class="w-full h-[48px] bg-apple-blue text-white font-medium text-[17px] rounded-standard border-none cursor-pointer transition-all duration-200 hover:opacity-90 active:bg-btn-active active:text-near-black disabled:opacity-50 disabled:cursor-not-allowed leading-[48px]"
          @click="handleLogin"
        >
          <span v-if="loading" class="flex items-center justify-center gap-2">
            <el-icon class="animate-spin"><Loading /></el-icon>
            登录中...
          </span>
          <span v-else>登录</span>
        </button>
      </div>
      
      <!-- Footer -->
      <div class="mt-8 text-center">
        <span class="text-[14px] text-text-tertiary tracking-[-0.224px]">还没有账号？</span>
        <button 
          type="button"
          class="ml-1 text-[14px] font-normal text-link-blue hover:underline underline-offset-2 transition-colors tracking-[-0.224px]"
          @click="router.push('/register')"
        >
          立即注册
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Apple Style Input Overrides */
:deep(.apple-input .el-input__wrapper) {
  background-color: #fafafc !important;
  border-radius: 11px !important;
  box-shadow: none !important;
  border: 3px solid rgba(0, 0, 0, 0.04) !important;
  padding: 0 14px !important;
  height: 48px !important;
}

:deep(.apple-input .el-input__inner) {
  color: #1d1d1f !important;
  font-size: 17px !important;
  font-weight: 400 !important;
  letter-spacing: -0.374px !important;
}

:deep(.apple-input .el-input__inner::placeholder) {
  color: rgba(0, 0, 0, 0.48) !important;
}

:deep(.apple-input .el-input__prefix) {
  margin-right: 10px !important;
}

/* Remove default form item margin */
:deep(.el-form-item) {
  margin-bottom: 0 !important;
}

:deep(.el-form-item__error) {
  color: #FF3B30 !important;
  font-size: 12px !important;
  padding-top: 4px !important;
  letter-spacing: -0.12px !important;
}
</style>
