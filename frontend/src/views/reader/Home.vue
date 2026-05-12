<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getBooks, getCategoryTree, aiSearchBooks } from '@/api/books'
import { getPublishedAnnouncements } from '@/api/announcements'
import imageCache from '@/utils/imageCache'

const router = useRouter()

const loading = ref(false)
const books = ref([])
const categories = ref([])
const announcements = ref([])

const searchParams = ref({
  search: '',
  category: '',
  page: 1,
  page_size: 10
})

const total = ref(0)
const coverUrls = ref({}) // 本地缓存的封面 URL 映射表

// 公告详情弹窗
const announcementVisible = ref(false)
const currentAnnouncement = ref({ title: '', content: '' })

async function fetchBooks() {
  loading.value = true
  try {
    const params = { ...searchParams.value, status: 1 }
    if (!params.category) delete params.category
    if (!params.search) delete params.search
    
    const data = await getBooks(params)
    const newBooks = data.results || []
    books.value = newBooks
    total.value = data.count || 0

    // 预加载封面到本地缓存
    const urlMap = await imageCache.preloadImages(newBooks)
    coverUrls.value = { ...coverUrls.value, ...urlMap }
  } catch (error) {
    console.error('获取图书失败:', error)
  } finally {
    loading.value = false
  }
}

function getCoverUrl(book) {
  return coverUrls.value[book.id] || book.cover_url || '/default-cover.svg'
}

async function fetchCategories() {
  try {
    const data = await getCategoryTree()
    categories.value = data || []
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

async function fetchAnnouncements() {
  try {
    const data = await getPublishedAnnouncements({ page_size: 5 })
    announcements.value = data.results || []
  } catch (error) {
    console.error('获取公告失败:', error)
  }
}

function handleSearch() {
  searchParams.value.page = 1
  fetchBooks()
}

function handlePageChange(page) {
  searchParams.value.page = page
  fetchBooks()
}

function goToDetail(id) {
  router.push(`/reader/book/${id}`)
}

function showAnnouncement(item) {
  currentAnnouncement.value = { title: item.title, content: item.content }
  announcementVisible.value = true
}

// ========== AI 智能检索 ==========
const aiChatOpen = ref(false)
const aiQuery = ref('')
const aiLoading = ref(false)
const aiMessages = ref([]) // { role: 'user'|'ai', content: string }
const chatBodyRef = ref(null)

function toggleAIChat() {
  aiChatOpen.value = !aiChatOpen.value
}

async function sendAIQuery() {
  const q = aiQuery.value.trim()
  if (!q || aiLoading.value) return

  aiMessages.value.push({ role: 'user', content: q })
  aiQuery.value = ''
  aiLoading.value = true
  scrollChatToBottom()

  try {
    const data = await aiSearchBooks(q)
    if (data.found && data.books && data.books.length > 0) {
      const lines = data.books.map(b => `《${b.title}》 ${b.author ? '- ' + b.author : ''}\n${b.reason || ''}`)
      aiMessages.value.push({ role: 'ai', content: '为您找到以下图书：\n\n' + lines.join('\n\n') })
    } else {
      aiMessages.value.push({ role: 'ai', content: data.message || '未查询到该类图书' })
    }
  } catch (err) {
    aiMessages.value.push({ role: 'ai', content: '检索失败，请稍后重试' })
  } finally {
    aiLoading.value = false
    scrollChatToBottom()
  }
}

function scrollChatToBottom() {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
  fetchAnnouncements()
})

onUnmounted(() => {
  // 释放 blob URL，避免内存泄漏
  imageCache.revokeUrls(coverUrls.value)
})
</script>

<template>
  <div class="home-container">
    <!-- 公告区域 - Apple Style -->
    <div v-if="announcements.length > 0" class="announcement-section">
      <el-carousel height="48px" direction="vertical" :autoplay="true" indicator-position="none">
        <el-carousel-item v-for="item in announcements" :key="item.id">
          <div class="announcement-item" @click="showAnnouncement(item)">
            <el-icon color="#0071e3" size="14"><Bell /></el-icon>
            <span class="announcement-title">{{ item.title }}</span>
            <span class="announcement-link">查看详情 &gt;</span>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
    
    <!-- 搜索区域 - Apple Filter Button Style -->
    <div class="search-section">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="flex-1 min-w-[200px]">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索书名、作者..."
            prefix-icon="Search"
            clearable
            class="apple-input"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
        </div>
        <div class="w-[180px]">
          <el-tree-select
            v-model="searchParams.category"
            :data="categories"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择分类"
            clearable
            check-strictly
            @change="handleSearch"
          />
        </div>
        <button 
          class="h-[40px] px-4 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]"
          @click="handleSearch"
        >
          搜索
        </button>
      </div>
    </div>
    
    <!-- 图书列表 - Apple Product Grid -->
    <div v-loading="loading" class="book-section">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
        <div 
          v-for="book in books" 
          :key="book.id" 
          class="book-card cursor-pointer group"
          @click="goToDetail(book.id)"
        >
          <div class="book-cover">
            <el-image
              :src="getCoverUrl(book)"
              fit="cover"
              class="cover-img"
            >
              <template #error>
                <div class="cover-placeholder">
                  <el-icon size="32" class="text-text-tertiary"><Reading /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          <div class="book-info">
            <h4 class="book-title" :title="book.title">{{ book.title }}</h4>
            <p class="book-author">{{ book.author }}</p>
            <span 
              class="book-status"
              :class="book.available_copies > 0 ? 'status-available' : 'status-unavailable'"
            >
              {{ book.available_copies > 0 ? `可借 ${book.available_copies}` : '暂无可借' }}
            </span>
          </div>
        </div>
      </div>
      
      <el-empty v-if="!loading && books.length === 0" description="暂无图书" />
      
      <!-- 分页 -->
      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="searchParams.page"
          :page-size="searchParams.page_size"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="handlePageChange"
        />
      </div>
    </div>
    
    <!-- 公告详情弹窗 -->
    <el-dialog v-model="announcementVisible" title="公告详情" width="500px" class="apple-dialog">
      <div class="announcement-detail">
        <h3>{{ currentAnnouncement.title }}</h3>
        <div class="h-px bg-[rgba(0,0,0,0.1)] my-4"></div>
        <p>{{ currentAnnouncement.content }}</p>
      </div>
      <template #footer>
        <button 
          class="px-4 py-2 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity"
          @click="announcementVisible = false"
        >
          关闭
        </button>
      </template>
    </el-dialog>

    <!-- AI 智能检索浮动框 -->
    <div class="ai-chat-wrapper">
      <!-- 触发按钮 -->
      <div v-if="!aiChatOpen" class="ai-chat-trigger" @click="toggleAIChat">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <!-- 对话框 -->
      <div v-if="aiChatOpen" class="ai-chat-box">
        <div class="ai-chat-header">
          <span>🤖 智能找书</span>
          <span class="ai-chat-close" @click="toggleAIChat">&times;</span>
        </div>
        <div ref="chatBodyRef" class="ai-chat-body">
          <div v-if="aiMessages.length === 0" class="ai-chat-placeholder">
            试试输入“我想看一本写动物的书”
          </div>
          <div v-for="(msg, idx) in aiMessages" :key="idx" 
               :class="['ai-msg', msg.role === 'user' ? 'ai-msg-user' : 'ai-msg-bot']">
            <div class="ai-msg-bubble">{{ msg.content }}</div>
          </div>
          <div v-if="aiLoading" class="ai-msg ai-msg-bot">
            <div class="ai-msg-bubble ai-typing">思考中...</div>
          </div>
        </div>
        <div class="ai-chat-footer">
          <input 
            v-model="aiQuery" 
            class="ai-chat-input" 
            placeholder="描述你想找的书..." 
            @keyup.enter="sendAIQuery"
          />
          <button class="ai-chat-send" :disabled="aiLoading" @click="sendAIQuery">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
}

.announcement-section {
  background: rgba(0, 113, 227, 0.06);
  border: none;
  border-radius: 11px;
  padding: 0 16px;
  margin-bottom: 24px;
}

.announcement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 48px;
  cursor: pointer;
}

.announcement-title {
  flex: 1;
  color: rgba(0, 0, 0, 0.8);
  font-size: 14px;
  letter-spacing: -0.224px;
}

.announcement-link {
  color: #0066cc;
  font-size: 12px;
  letter-spacing: -0.12px;
}

.search-section {
  background: #fafafc;
  padding: 16px;
  border-radius: 11px;
  border: 3px solid rgba(0, 0, 0, 0.04);
  margin-bottom: 24px;
}

.book-section {
  min-height: 400px;
}

.book-card {
  transition: transform 200ms ease;
}

.book-card:hover {
  transform: translateY(-2px);
}

.book-cover {
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f5f5f7;
  border-radius: 8px;
  margin-bottom: 10px;
}

.cover-img {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f7;
}

.book-info {
  padding: 0 2px;
}

.book-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.224px;
  line-height: 1.29;
}

.book-author {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.48);
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.12px;
  line-height: 1.33;
}

.book-status {
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 980px;
  letter-spacing: -0.08px;
  line-height: 1.47;
}

.status-available {
  background: rgba(0, 125, 72, 0.1);
  color: #007D48;
}

.status-unavailable {
  background: rgba(255, 59, 48, 0.1);
  color: #FF3B30;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.announcement-detail h3 {
  margin: 0 0 4px;
  font-size: 21px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: 0.231px;
  line-height: 1.19;
}

.announcement-detail p {
  margin: 0;
  line-height: 1.47;
  color: rgba(0, 0, 0, 0.8);
  letter-spacing: -0.374px;
  white-space: pre-wrap;
}

/* Apple Input */
:deep(.apple-input .el-input__wrapper) {
  background-color: #fafafc !important;
  border-radius: 11px !important;
  box-shadow: none !important;
  border: 3px solid rgba(0, 0, 0, 0.04) !important;
  height: 40px !important;
}

:deep(.apple-input .el-input__inner) {
  color: #1d1d1f !important;
  font-size: 14px !important;
  letter-spacing: -0.224px !important;
}

:deep(.apple-input .el-input__inner::placeholder) {
  color: rgba(0, 0, 0, 0.48) !important;
}

/* AI 智能检索浮动框 */
.ai-chat-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.ai-chat-trigger {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #0071e3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 113, 227, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}

.ai-chat-trigger:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 20px rgba(0, 113, 227, 0.5);
}

.ai-chat-box {
  width: 320px;
  height: 420px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f5f7;
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.ai-chat-close {
  font-size: 20px;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.4);
  line-height: 1;
}

.ai-chat-close:hover {
  color: #1d1d1f;
}

.ai-chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-chat-placeholder {
  text-align: center;
  color: rgba(0, 0, 0, 0.35);
  font-size: 13px;
  margin-top: 60px;
}

.ai-msg {
  display: flex;
}

.ai-msg-user {
  justify-content: flex-end;
}

.ai-msg-bot {
  justify-content: flex-start;
}

.ai-msg-bubble {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-msg-user .ai-msg-bubble {
  background: #0071e3;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-msg-bot .ai-msg-bubble {
  background: #f0f0f5;
  color: #1d1d1f;
  border-bottom-left-radius: 4px;
}

.ai-typing {
  color: rgba(0, 0, 0, 0.4);
  font-style: italic;
}

.ai-chat-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: #fafafc;
}

.ai-chat-input {
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.ai-chat-input:focus {
  border-color: #0071e3;
}

.ai-chat-send {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #0071e3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s;
}

.ai-chat-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-chat-send:not(:disabled):hover {
  opacity: 0.85;
}
</style>
