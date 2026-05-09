// 仪表盘统计接口
import request from './request'

/**
 * 获取统计数据
 */
export function getDashboardStats() {
  return request.get('/api/dashboard/stats/')
}

/**
 * 获取最近数据
 */
export function getDashboardRecent() {
  return request.get('/api/dashboard/recent/')
}
