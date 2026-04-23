# 图书封面本地缓存方案

## 一、技术概述

本方案使用浏览器内置的 **IndexedDB + localStorage** 实现图书封面图片的本地持久化缓存，无需修改后端代码，无需引入任何第三方库。

| 技术 | 用途 |
|------|------|
| **IndexedDB** | 存储图片二进制数据（Blob） |
| **localStorage** | 存储缓存元数据（URL + 缓存时间） |
| **Blob URL** | 将 Blob 转为本地可用的 `blob://` 地址用于 `<img>` 展示 |
| **Fetch API** | 从网络拉取图片为 Blob 格式 |

---

## 二、代码目录

```
frontend/src/
├── utils/
│   └── imageCache.js          # 核心缓存工具类（新增）
├── views/
│   └── reader/
│       ├── Home.vue            # 图书列表页（已接入缓存）
│       └── BookDetail.vue      # 图书详情页（已接入缓存）
```

---

## 三、数据存储位置

所有数据存储在**用户本地浏览器**中，不经过服务器，不影响后端数据库。

### 1. IndexedDB（存储图片二进制）

```
浏览器 IndexedDB
└── 数据库：BookCornerDB（版本 1）
    └── 对象仓库：bookCovers
        ├── id        → 图书 ID（主键，字符串）
        ├── blob      → 图片 Blob 对象（二进制数据）
        ├── url       → 图片网络地址
        └── timestamp → 缓存写入时间戳（毫秒）
```

**查看方式：** 打开浏览器开发者工具（F12）→ Application → IndexedDB → BookCornerDB → bookCovers

### 2. localStorage（存储缓存元数据）

```
Key:   book_cover_{bookId}
Value: {
  "url": "https://example.com/covers/book123.jpg",
  "cachedAt": 1711234567890
}
```

**作用：** 在访问 IndexedDB 之前快速判断是否存在有效缓存，避免不必要的数据库读取。

**查看方式：** 开发者工具 → Application → Local Storage

---

## 四、缓存策略

### 读取流程

```
请求图书封面
    │
    ▼
localStorage 是否有该 bookId 的缓存记录？
    │
    ├─ 否 ──────────────────────────────────────────────────┐
    │                                                       │
    ▼                                                       ▼
URL 是否变更或缓存是否超过 7 天？                    fetch 网络图片 → Blob
    │                   │                                   │
    │ 否                │ 是（过期）                        ▼
    ▼                   └──────────────────────────→  存入 IndexedDB
IndexedDB 读取 Blob                                  更新 localStorage
    │                                                       │
    ▼                                                       ▼
URL.createObjectURL(blob)                        URL.createObjectURL(blob)
    │                                                       │
    └──────────────────────┬────────────────────────────────┘
                           ▼
                    <el-image :src="blobUrl">
```

### 缓存参数

| 参数 | 值 | 说明 |
|------|----|------|
| 缓存有效期 | 7 天 | 超期后重新从网络拉取 |
| 批量并发数 | 5 | 列表页每批同时预加载 5 张图片 |
| 降级策略 | 返回原始 URL | IndexedDB 不可用时自动降级 |

---

## 五、核心代码

### imageCache.js 主要方法

```javascript
// 获取单张图片（优先缓存）
await imageCache.getImage(bookId, imageUrl)
// 返回：blob://... 或原始 URL（降级）

// 批量预加载图书列表封面
const urlMap = await imageCache.preloadImages(books)
// 返回：{ [bookId]: 'blob://...' }

// 释放 blob URL（组件销毁时调用，防内存泄漏）
imageCache.revokeUrls(urlMap)
```

### Home.vue 接入方式

```javascript
// 加载图书列表后预缓存封面
const newBooks = data.results || []
books.value = newBooks
const urlMap = await imageCache.preloadImages(newBooks)
coverUrls.value = { ...coverUrls.value, ...urlMap }

// 模板中使用本地缓存 URL
function getCoverUrl(book) {
  return coverUrls.value[book.id] || book.cover_url || '/default-cover.png'
}

// 组件销毁时释放内存
onUnmounted(() => {
  imageCache.revokeUrls(coverUrls.value)
})
```

### BookDetail.vue 接入方式

```javascript
// 获取图书详情后缓存封面
const data = await getBook(route.params.id)
book.value = data
if (data.cover_url) {
  coverUrl.value = await imageCache.getImage(data.id, data.cover_url)
}

// 组件销毁时释放内存
onUnmounted(() => {
  if (coverUrl.value && coverUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(coverUrl.value)
  }
})
```

---

## 六、性能对比

| 场景 | 无缓存 | 有缓存 |
|------|--------|--------|
| 首次加载 | 网络请求（~200ms） | 网络请求 + 写入本地 |
| 二次访问 | 网络请求（~200ms） | 本地读取（~5ms，提升 40 倍） |
| 翻页后返回 | 重新请求网络 | 秒显示 |
| 断网访问 | 无法显示 | 正常显示（已缓存的） |
| 流量消耗 | 每次都产生 | 仅首次产生 |

---

## 七、注意事项

1. **同源限制**：IndexedDB 数据仅在同一域名下可访问，开发环境（`localhost:5173`）与生产环境数据互不干扰。

2. **存储容量**：IndexedDB 容量通常在 50MB 以上（具体由浏览器和磁盘空间决定），远超 localStorage 的 5MB 上限，适合存储图片文件。

3. **内存管理**：每次调用 `URL.createObjectURL()` 都会占用内存，必须在组件销毁时调用 `URL.revokeObjectURL()` 释放，已在各组件的 `onUnmounted` 中处理。

4. **缓存失效**：当图书封面 URL 发生变更时（`meta.url !== imageUrl`），缓存自动视为无效并重新拉取。

5. **零后端改动**：本方案完全在前端实现，无需修改 Django 后端任何代码，无需添加任何 Python 依赖。
