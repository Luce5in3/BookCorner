// 公告相关接口
import request from './request'

/**
 * 获取公告列表（管理员）
 * @param {Object} params { page, page_size, status }
 */
export function getAnnouncements(params) {
  return request.get('/api/announcements/', { params })
}

/**
 * 获取已发布公告列表（公开）
 */
export function getPublishedAnnouncements(params) {
  return request.get('/api/announcements/published/', { params })
}

/**
 * 获取公告详情
 */
export function getAnnouncement(id) {
  return request.get(`/api/announcements/${id}/`)
}

/**
 * 创建公告
 * @param {Object} data { title, content }
 */
export function createAnnouncement(data) {
  return request.post('/api/announcements/', data)
}

/**
 * 更新公告
 */
export function updateAnnouncement(id, data) {
  return request.put(`/api/announcements/${id}/`, data)
}

/**
 * 删除公告
 */
export function deleteAnnouncement(id) {
  return request.delete(`/api/announcements/${id}/`)
}

/**
 * 发布公告
 * @param {number} id 公告 ID
 */
export function publishAnnouncement(id) {
  return request.post(`/api/announcements/${id}/publish/`)
}

/**
 * 下架公告
 * @param {number} id 公告 ID
 */
export function unpublishAnnouncement(id) {
  return request.post(`/api/announcements/${id}/unpublish/`)
}
