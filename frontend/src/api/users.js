// 用户相关接口
import request from './request'

/**
 * 获取用户列表（管理员）
 * @param {Object} params { page, page_size, search, role, status }
 */
export function getUsers(params) {
  return request.get('/api/users/', { params })
}

/**
 * 获取用户详情
 */
export function getUser(id) {
  return request.get(`/api/users/${id}/`)
}

/**
 * 搜索读者（用于选择框）
 * @param {string} search 搜索关键词（用户名/姓名/手机号）
 */
export function searchReaders(search) {
  return request.get('/api/users/', { 
    params: { search, role: 0, status: 1, page_size: 20 } 
  })
}
