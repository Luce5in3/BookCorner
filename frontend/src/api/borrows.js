// 借阅相关接口
import request from './request'

/**
 * 获取借阅列表
 * @param {Object} params { page, page_size, user, status }
 */
export function getBorrows(params) {
  return request.get('/api/borrows/', { params })
}

/**
 * 获取我的借阅列表
 */
export function getMyBorrows(params) {
  return request.get('/api/borrows/my/', { params })
}

/**
 * 获取借阅详情
 */
export function getBorrow(id) {
  return request.get(`/api/borrows/${id}/`)
}

/**
 * 借书
 * @param {Object} data { book_copy_id, user_id }
 */
export function borrowBook(data) {
  return request.post('/api/borrows/borrow/', data)
}

/**
 * 还书
 * @param {number} id 借阅记录 ID
 */
export function returnBook(id) {
  return request.post(`/api/borrows/${id}/return/`)
}

/**
 * 续借
 * @param {number} id 借阅记录 ID
 */
export function renewBook(id) {
  return request.post(`/api/borrows/${id}/renew/`)
}

/**
 * 标记丢失
 * @param {number} id 借阅记录 ID
 */
export function markLost(id) {
  return request.post(`/api/borrows/${id}/lost/`)
}
