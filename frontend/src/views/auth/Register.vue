<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  real_name: '',
  email: '',
  phone: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度为 6-20 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

async function handleRegister() {
  try {
    await formRef.value.validate()
    loading.value = true
    
    const { confirmPassword, ...data } = form
    await register(data)
    
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-apple-gray">
    <div class="w-full max-w-[500px] px-6">
      <div class="bg-apple-white rounded-large p-10 shadow-card">
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-14 h-14 bg-apple-black rounded-full mb-5">
            <el-icon size="28" color="#FFFFFF"><Reading /></el-icon>
          </div>
          <h1 class="text-[28px] font-semibold text-near-black leading-[1.14] tracking-[0.196px] mb-1">注册账号</h1>
          <p class="text-[14px] text-text-secondary tracking-[-0.224px]">加入图书角，开启阅读之旅</p>
        </div>
        
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="register-form apple-form"
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="用户名" prop="username">
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="真实姓名" prop="real_name">
                <el-input
                  v-model="form.real_name"
                  placeholder="请输入真实姓名"
                  prefix-icon="Postcard"
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  show-password
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="form.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  prefix-icon="Lock"
                  show-password
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="form.email"
                  placeholder="请输入邮箱（选填）"
                  prefix-icon="Message"
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input
                  v-model="form.phone"
                  placeholder="请输入手机号（选填）"
                  prefix-icon="Phone"
                  class="apple-input"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item class="!mt-2">
            <button
              type="button"
              :disabled="loading"
              class="w-full h-11 bg-apple-blue text-white font-normal text-[17px] rounded-standard border-none cursor-pointer transition-all duration-200 hover:opacity-90 active:bg-btn-active active:text-near-black disabled:opacity-50 disabled:cursor-not-allowed"
              @click="handleRegister"
            >
              <span v-if="loading" class="flex items-center justify-center gap-2">
                <el-icon class="animate-spin"><Loading /></el-icon>
                注册中...
              </span>
              <span v-else>注册</span>
            </button>
          </el-form-item>
        </el-form>
        
        <div class="text-center mt-6">
          <span class="text-[14px] text-text-tertiary tracking-[-0.224px]">已有账号？</span>
          <button 
            type="button"
            class="ml-1 text-[14px] font-normal text-link-blue hover:underline underline-offset-2 transition-colors tracking-[-0.224px]"
            @click="router.push('/login')"
          >
            立即登录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.apple-form :deep(.el-form-item__label) {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: #1d1d1f !important;
  letter-spacing: -0.224px !important;
  padding-bottom: 4px !important;
}

.apple-form :deep(.el-form-item) {
  margin-bottom: 16px !important;
}

.apple-form :deep(.apple-input .el-input__wrapper) {
  background-color: #fafafc !important;
  border-radius: 11px !important;
  box-shadow: none !important;
  border: 3px solid rgba(0, 0, 0, 0.04) !important;
  padding: 0 14px !important;
  height: 44px !important;
}

.apple-form :deep(.apple-input .el-input__inner) {
  color: #1d1d1f !important;
  font-size: 17px !important;
  font-weight: 400 !important;
  letter-spacing: -0.374px !important;
}

.apple-form :deep(.apple-input .el-input__inner::placeholder) {
  color: rgba(0, 0, 0, 0.48) !important;
}

.apple-form :deep(.el-form-item__error) {
  color: #FF3B30 !important;
  font-size: 12px !important;
  letter-spacing: -0.12px !important;
}
</style>
