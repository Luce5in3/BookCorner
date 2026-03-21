// 图书、分类、副本相关接口
import request from './request'

// ========== 分类接口 ==========

/**
 * 获取分类树
 */
export function getCategoryTree() {
  return request.get('/api/categories/')
}

/**
 * 获取分类列表
 */
export function getCategories(params) {
  return request.get('/api/categories/', { params })
}

/**
 * 创建分类
 */
export function createCategory(data) {
  return request.post('/api/categories/', data)
}

/**
 * 更新分类
 */
export function updateCategory(id, data) {
  return request.put(`/api/categories/${id}/`, data)
}

/**
 * 删除分类
 */
export function deleteCategory(id) {
  return request.delete(`/api/categories/${id}/`)
}

// ========== 图书接口 ==========

/**
 * 获取图书列表
 * @param {Object} params { page, page_size, search, category, status }
 */
export function getBooks(params) {
  return request.get('/api/books/', { params })
}

/**
 * 获取图书详情
 */
export function getBook(id) {
  return request.get(`/api/books/${id}/`)
}

/**
 * 创建图书
 */
export function createBook(data) {
  return request.post('/api/books/', data)
}

/**
 * 更新图书
 */
export function updateBook(id, data) {
  return request.put(`/api/books/${id}/`, data)
}

/**
 * 删除图书
 */
export function deleteBook(id) {
  return request.delete(`/api/books/${id}/`)
}

/**
 * 上架图书
 */
export function publishBook(id) {
  return request.post(`/api/books/${id}/toggle-status/`)
}

/**
 * 下架图书
 */
export function unpublishBook(id) {
  return request.post(`/api/books/${id}/toggle-status/`)
}

// ========== 副本接口 ==========

/**
 * 获取副本列表
 * @param {Object} params { page, page_size, book, status }
 */
export function getCopies(params) {
  return request.get('/api/copies/', { params })
}

/**
 * 获取副本详情
 */
export function getCopy(id) {
  return request.get(`/api/copies/${id}/`)
}

/**
 * 创建副本
 */
export function createCopy(data) {
  return request.post('/api/copies/', data)
}

/**
 * 更新副本
 */
export function updateCopy(id, data) {
  return request.put(`/api/copies/${id}/`, data)
}

/**
 * 删除副本
 */
export function deleteCopy(id) {
  return request.delete(`/api/copies/${id}/`)
}
