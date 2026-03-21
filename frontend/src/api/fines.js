// 罚款相关接口
import request from './request'

/**
 * 获取罚款列表
 * @param {Object} params { page, page_size, user, status }
 */
export function getFines(params) {
  return request.get('/api/fines/', { params })
}

/**
 * 获取我的罚款列表
 */
export function getMyFines(params) {
  return request.get('/api/fines/my/', { params })
}

/**
 * 获取罚款详情
 */
export function getFine(id) {
  return request.get(`/api/fines/${id}/`)
}

/**
 * 缴纳罚款
 * @param {number} id 罚款记录 ID
 */
export function payFine(id) {
  return request.post(`/api/fines/${id}/pay/`)
}

/**
 * 免除罚款（管理员）
 * @param {number} id 罚款记录 ID
 */
export function waiveFine(id) {
  return request.post(`/api/fines/${id}/waive/`)
}
