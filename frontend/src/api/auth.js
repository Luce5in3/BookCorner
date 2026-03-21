// 认证相关接口
import request from './request'

/**
 * 用户登录
 * @param {Object} data { username, password }
 */
export function login(data) {
  return request.post('/api/auth/login/', data)
}

/**
 * 用户注册
 * @param {Object} data { username, password, real_name, email, phone }
 */
export function register(data) {
  return request.post('/api/auth/register/', data)
}

/**
 * 刷新 token
 * @param {string} refresh refresh_token
 */
export function refreshToken(refresh) {
  return request.post('/api/auth/refresh/', { refresh })
}

/**
 * 获取当前用户信息
 */
export function getUserInfo() {
  return request.get('/api/auth/me/')
}

/**
 * 修改密码
 * @param {Object} data { old_password, new_password }
 */
export function changePassword(data) {
  return request.put('/api/auth/password/', data)
}
