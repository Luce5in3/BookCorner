// Axios 实例封装
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '@/utils/token'
import router from '@/router'

// 创建 Axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 是否正在刷新 token
let isRefreshing = false
// 等待刷新 token 的请求队列
let requestQueue = []

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    
    // 统一处理响应格式 { code, message, data }
    // 支持 200 和 201 状态码
    if (res.code !== 200 && res.code !== 201) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res.data
  },
  async (error) => {
    const { response, config } = error
    
    // 401 未授权 - 尝试刷新 token
    if (response?.status === 401) {
      const refreshToken = getRefreshToken()
      
      // 没有 refresh token，可能是登录失败或其他无 token 的 401
      if (!refreshToken) {
        clearTokens()
        // 显示后端返回的具体错误信息
        const message = response?.data?.message || '认证失败，请重新登录'
        ElMessage.error(message)
        // 仅在非登录页时跳转
        if (!config.url?.includes('/auth/login/')) {
          router.push('/login')
        }
        return Promise.reject(error)
      }
      
      // 防止多次刷新 token
      if (!isRefreshing) {
        isRefreshing = true
        
        try {
          // 刷新 token
          const res = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh/`,
            { refresh: refreshToken }
          )
          
          if (res.data.code === 200) {
            const { access } = res.data.data
            setTokens(access, refreshToken)
            
            // 重试队列中的请求
            requestQueue.forEach(cb => cb(access))
            requestQueue = []
            
            // 重试当前请求
            config.headers.Authorization = `Bearer ${access}`
            return request(config)
          } else {
            throw new Error('刷新 token 失败')
          }
        } catch (err) {
          // 刷新失败，清除 token 并跳转登录
          clearTokens()
          requestQueue = []
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          return Promise.reject(err)
        } finally {
          isRefreshing = false
        }
      } else {
        // 正在刷新 token，将请求加入队列
        return new Promise((resolve) => {
          requestQueue.push((token) => {
            config.headers.Authorization = `Bearer ${token}`
            resolve(request(config))
          })
        })
      }
    }
    
    // 其他错误
    const message = response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
