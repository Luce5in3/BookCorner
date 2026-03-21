// 格式化工具
import dayjs from 'dayjs'

/**
 * 格式化日期时间
 * @param {string|Date} date 日期
 * @param {string} format 格式，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns {string}
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 * @param {string|Date} date 日期
 * @returns {string}
 */
export function formatDate(date) {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化金额
 * @param {number} amount 金额
 * @param {number} decimals 小数位数，默认 2
 * @returns {string}
 */
export function formatMoney(amount, decimals = 2) {
  if (amount === null || amount === undefined) return '-'
  return `¥${Number(amount).toFixed(decimals)}`
}

/**
 * 格式化金额（不带货币符号）
 * @param {number} amount 金额
 * @param {number} decimals 小数位数，默认 2
 * @returns {string}
 */
export function formatAmount(amount, decimals = 2) {
  if (amount === null || amount === undefined) return '-'
  return Number(amount).toFixed(decimals)
}

// 用户角色
export const USER_ROLE = {
  0: '读者',
  1: '管理员',
  2: '超级管理员'
}

// 用户状态
export const USER_STATUS = {
  0: '禁用',
  1: '正常'
}

// 图书状态
export const BOOK_STATUS = {
  0: '下架',
  1: '上架'
}

// 图书副本状态
export const COPY_STATUS = {
  0: '注销',
  1: '在馆',
  2: '借出',
  3: '预约锁定',
  4: '丢失'
}

// 图书副本品相
export const COPY_CONDITION = {
  1: '全新',
  2: '良好',
  3: '一般',
  4: '破损'
}

// 借阅状态
export const BORROW_STATUS = {
  0: '已还',
  1: '借阅中',
  2: '逾期',
  3: '丢失'
}

// 预约状态
export const RESERVATION_STATUS = {
  0: '已取消',
  1: '预约中',
  2: '已到馆',
  3: '已完成',
  4: '已过期'
}

// 罚款状态
export const FINE_STATUS = {
  0: '待缴',
  1: '已缴',
  2: '已免除'
}

// 公告状态
export const ANNOUNCEMENT_STATUS = {
  0: '草稿',
  1: '已发布',
  2: '已下架'
}

/**
 * 获取状态标签类型（Element Plus tag type）
 */
export function getStatusTagType(status, type) {
  const typeMap = {
    user: { 0: 'danger', 1: 'success' },
    book: { 0: 'info', 1: 'success' },
    copy: { 0: 'info', 1: 'success', 2: 'warning', 3: 'primary', 4: 'danger' },
    borrow: { 0: 'info', 1: 'success', 2: 'danger', 3: 'danger' },
    reservation: { 0: 'info', 1: 'primary', 2: 'success', 3: 'success', 4: 'warning' },
    fine: { 0: 'danger', 1: 'success', 2: 'info' },
    announcement: { 0: 'info', 1: 'success', 2: 'warning' }
  }
  return typeMap[type]?.[status] || 'info'
}
