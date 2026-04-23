/**
 * 图片缓存工具 - IndexedDB + localStorage
 * 将图书封面图片以 Blob 形式缓存在浏览器本地，提升二次访问速度
 */

const DB_NAME = 'BookCornerDB'
const STORE_NAME = 'bookCovers'
const DB_VERSION = 1
const MAX_AGE = 7 * 24 * 60 * 60 * 1000 // 7 天有效期
const BATCH_SIZE = 5 // 并发预加载数量

class ImageCache {
  constructor() {
    this.db = null
    this._initPromise = null
  }

  /**
   * 初始化 IndexedDB（单例，避免重复打开）
   */
  init() {
    if (this._initPromise) return this._initPromise

    this._initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        console.error('[ImageCache] IndexedDB 打开失败:', request.error)
        this._initPromise = null
        reject(request.error)
      }

      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }

      request.onupgradeneeded = (event) => {
        const db = event.target.result
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
          store.createIndex('timestamp', 'timestamp', { unique: false })
        }
      }
    })

    return this._initPromise
  }

  /**
   * 获取图片本地 Blob URL
   * 优先从缓存读取，缓存不存在或过期则重新拉取并缓存
   *
   * @param {string|number} bookId - 图书 ID
   * @param {string} imageUrl - 图片网络地址
   * @returns {Promise<string>} 本地 blob URL 或原始 URL（降级）
   */
  async getImage(bookId, imageUrl) {
    if (!imageUrl) return ''

    const id = String(bookId)

    try {
      await this.init()

      // 1. 读取 localStorage 元数据，判断是否存在有效缓存
      const metaRaw = localStorage.getItem(`book_cover_${id}`)
      if (metaRaw) {
        const meta = JSON.parse(metaRaw)
        const isExpired = Date.now() - meta.cachedAt > MAX_AGE
        const isSameUrl = meta.url === imageUrl

        if (!isExpired && isSameUrl) {
          // 2. 从 IndexedDB 读取 Blob
          const blob = await this._getBlob(id)
          if (blob) {
            return URL.createObjectURL(blob)
          }
        }
      }

      // 3. 无缓存或已过期，从网络加载
      const blob = await this._fetchBlob(imageUrl)
      await this._save(id, blob, imageUrl)
      return URL.createObjectURL(blob)

    } catch (error) {
      console.warn(`[ImageCache] 获取图片失败 (bookId=${bookId}):`, error)
      // 降级：返回原始 URL
      return imageUrl
    }
  }

  /**
   * 批量预加载图片（并发控制）
   * @param {Array<{id, cover_url}>} books - 图书列表
   * @returns {Promise<Object>} bookId -> localUrl 映射表
   */
  async preloadImages(books) {
    const validBooks = books.filter(b => b.cover_url)
    const result = {}

    for (let i = 0; i < validBooks.length; i += BATCH_SIZE) {
      const batch = validBooks.slice(i, i + BATCH_SIZE)
      await Promise.all(
        batch.map(async (book) => {
          try {
            result[book.id] = await this.getImage(book.id, book.cover_url)
          } catch (e) {
            result[book.id] = book.cover_url
          }
        })
      )
    }

    return result
  }

  /**
   * 释放 blob URL，防止内存泄漏
   * @param {Object} urlMap - bookId -> blobUrl 映射表
   */
  revokeUrls(urlMap) {
    Object.values(urlMap).forEach(url => {
      if (url && url.startsWith('blob:')) {
        URL.revokeObjectURL(url)
      }
    })
  }

  /**
   * 清除指定图书的缓存
   * @param {string|number} bookId
   */
  async removeCache(bookId) {
    const id = String(bookId)
    localStorage.removeItem(`book_cover_${id}`)

    try {
      await this.init()
      await new Promise((resolve, reject) => {
        const tx = this.db.transaction([STORE_NAME], 'readwrite')
        tx.objectStore(STORE_NAME).delete(id)
        tx.oncomplete = resolve
        tx.onerror = () => reject(tx.error)
      })
    } catch (error) {
      console.warn('[ImageCache] 删除缓存失败:', error)
    }
  }

  /**
   * 清除所有封面缓存
   */
  async clearAll() {
    // 清 localStorage
    Object.keys(localStorage)
      .filter(k => k.startsWith('book_cover_'))
      .forEach(k => localStorage.removeItem(k))

    // 清 IndexedDB
    try {
      await this.init()
      await new Promise((resolve, reject) => {
        const tx = this.db.transaction([STORE_NAME], 'readwrite')
        tx.objectStore(STORE_NAME).clear()
        tx.oncomplete = resolve
        tx.onerror = () => reject(tx.error)
      })
    } catch (error) {
      console.warn('[ImageCache] 清除缓存失败:', error)
    }
  }

  // ---------- 内部方法 ----------

  async _getBlob(id) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction([STORE_NAME], 'readonly')
      const request = tx.objectStore(STORE_NAME).get(id)
      request.onsuccess = () => resolve(request.result?.blob || null)
      request.onerror = () => reject(request.error)
    })
  }

  async _save(id, blob, url) {
    await new Promise((resolve, reject) => {
      const tx = this.db.transaction([STORE_NAME], 'readwrite')
      tx.objectStore(STORE_NAME).put({ id, blob, url, timestamp: Date.now() })
      tx.oncomplete = resolve
      tx.onerror = () => reject(tx.error)
    })

    localStorage.setItem(`book_cover_${id}`, JSON.stringify({
      url,
      cachedAt: Date.now()
    }))
  }

  async _fetchBlob(url) {
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return await response.blob()
  }
}

export default new ImageCache()
