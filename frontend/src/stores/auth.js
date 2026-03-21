// 用户认证状态管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getUserInfo } from '@/api/auth'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '@/utils/token'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const userInfo = ref(null)
  const accessToken = ref(getAccessToken())
  const refreshToken = ref(getRefreshToken())

  // 计算属性
  const isLoggedIn = computed(() => !!accessToken.value)
  const isAdmin = computed(() => userInfo.value?.role >= 1)
  const isSuperAdmin = computed(() => userInfo.value?.role >= 2)
  const userRole = computed(() => userInfo.value?.role ?? -1)

  // 登录
  async function login(credentials) {
    const data = await loginApi(credentials)
    accessToken.value = data.access
    refreshToken.value = data.refresh
    setTokens(data.access, data.refresh)
    
    // 获取用户信息
    await fetchUserInfo()
    
    return data
  }

  // 退出登录
  function logout() {
    userInfo.value = null
    accessToken.value = null
    refreshToken.value = null
    clearTokens()
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (!accessToken.value) return null
    try {
      const data = await getUserInfo()
      userInfo.value = data
      return data
    } catch (error) {
      logout()
      throw error
    }
  }

  // 刷新 token 后更新本地状态
  function updateAccessToken(token) {
    accessToken.value = token
  }

  // 初始化：页面刷新时从 localStorage 恢复状态
  async function init() {
    if (accessToken.value && !userInfo.value) {
      try {
        await fetchUserInfo()
      } catch (error) {
        console.error('初始化获取用户信息失败:', error)
      }
    }
  }

  return {
    userInfo,
    accessToken,
    refreshToken,
    isLoggedIn,
    isAdmin,
    isSuperAdmin,
    userRole,
    login,
    logout,
    fetchUserInfo,
    updateAccessToken,
    init
  }
})
