// 预约相关接口
import request from './request'

/**
 * 获取预约列表（管理员）
 * @param {Object} params { page, page_size, user, book, status }
 */
export function getReservations(params) {
  return request.get('/api/reservations/list/', { params })
}

/**
 * 获取我的预约列表
 */
export function getMyReservations(params) {
  return request.get('/api/reservations/my/', { params })
}

/**
 * 获取预约详情
 */
export function getReservation(id) {
  return request.get(`/api/reservations/${id}/`)
}

/**
 * 创建预约
 * @param {Object} data { book_id }
 */
export function createReservation(data) {
  return request.post('/api/reservations/', data)
}

/**
 * 取消预约
 * @param {number} id 预约记录 ID
 */
export function cancelReservation(id) {
  return request.post(`/api/reservations/${id}/cancel/`)
}

/**
 * 通知到馆（管理员）
 * @param {number} id 预约记录 ID
 */
export function notifyReservation(id) {
  return request.post(`/api/reservations/${id}/notify/`)
}

/**
 * 完成预约（管理员）
 * @param {number} id 预约记录 ID
 */
export function completeReservation(id) {
  return request.post(`/api/reservations/${id}/complete/`)
}
