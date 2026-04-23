<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { getBook, generateDescription } from '@/api/books'
import { createReservation, getMyReservations } from '@/api/reservations'
import { formatDate, formatMoney, BOOK_STATUS } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import imageCache from '@/utils/imageCache'

const route = useRoute()
const loading = ref(false)
const book = ref(null)
const isReserved = ref(false)  // 是否已预约
const coverUrl = ref('')  // 本地缓存的封面 URL
const aiLoading = ref(false)  // AI 简介生成中
const aiDescription = ref('')  // AI 生成的简介
const aiKeywords = ref('')  // 用户关注的关键词

async function fetchBook() {
  loading.value = true
  try {
    const data = await getBook(route.params.id)
    book.value = data
    // 加载封面缓存
    if (data.cover_url) {
      coverUrl.value = await imageCache.getImage(data.id, data.cover_url)
    }
    // 检查是否已预约
    await checkReservation()
  } catch (error) {
    console.error('获取图书详情失败:', error)
  } finally {
    loading.value = false
  }
}

async function checkReservation() {
  try {
    const data = await getMyReservations({ status: 1, page_size: 100 })  // status=1 等待中
    const reservations = data.results || data || []
    isReserved.value = reservations.some(r => r.book_id === book.value?.id)
  } catch (error) {
    console.error('检查预约状态失败:', error)
  }
}

async function handleReserve() {
  try {
    await ElMessageBox.confirm('确定要预约这本书吗？', '预约确认', {
      confirmButtonText: '确定预约',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await createReservation({ book_id: book.value.id })
    ElMessage.success('预约成功！书籍到馆后会通知您')
    fetchBook()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('预约失败:', error)
    }
  }
}

async function handleGenerateDescription() {
  aiLoading.value = true
  try {
    const data = await generateDescription(book.value.id, aiKeywords.value)
    aiDescription.value = data.description
    book.value.description = data.description
    ElMessage.success('AI 简介生成成功')
  } catch (error) {
    console.error('AI 简介生成失败:', error)
    ElMessage.error(error?.response?.data?.message || 'AI 简介生成失败，请稍后重试')
  } finally {
    aiLoading.value = false
  }
}

onMounted(() => {
  fetchBook()
})

onUnmounted(() => {
  // 释放 blob URL，避免内存泄漏
  if (coverUrl.value && coverUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(coverUrl.value)
  }
})
</script>

<template>
  <div v-loading="loading" class="detail-container">
    <template v-if="book">
      <!-- Hero Section - Apple Product Hero Module -->
      <div class="bg-apple-black rounded-large p-8 mb-6">
        <div class="flex flex-col md:flex-row gap-8 items-start">
          <!-- 封面 -->
          <div class="w-full md:w-[220px] flex-shrink-0">
            <div class="book-cover">
              <el-image
                :src="coverUrl || book.cover_url || '/default-cover.png'"
                fit="cover"
                class="cover-img"
              >
                <template #error>
                  <div class="cover-placeholder">
                    <el-icon size="60" class="text-white/32"><Reading /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </div>
          
          <!-- 详情 -->
          <div class="flex-1 text-white">
            <h1 class="text-[40px] font-semibold leading-[1.10] tracking-[-0.28px] mb-3">{{ book.title }}</h1>
            <p class="text-[21px] font-normal leading-[1.19] tracking-[0.231px] text-white/80 mb-6">{{ book.author }}</p>
            
            <!-- 状态标签 -->
            <div class="flex gap-3 mb-6">
              <span 
                class="inline-flex items-center px-3 py-1 rounded-pill text-[12px] tracking-[-0.12px]"
                :class="book.status === 1 ? 'bg-[rgba(0,125,72,0.2)] text-[#4cd964]' : 'bg-white/10 text-white/48'"
              >
                {{ BOOK_STATUS[book.status] }}
              </span>
              <span 
                class="inline-flex items-center px-3 py-1 rounded-pill text-[12px] tracking-[-0.12px]"
                :class="book.available_copies > 0 ? 'bg-[rgba(0,125,72,0.2)] text-[#4cd964]' : 'bg-[rgba(255,59,48,0.2)] text-[#ff6b6b]'"
              >
                可借 {{ book.available_copies }} / 总 {{ book.total_copies }}
              </span>
            </div>
            
            <!-- 详情信息 -->
            <div class="grid grid-cols-2 gap-x-8 gap-y-3 mb-6">
              <div v-if="book.isbn" class="detail-field">
                <span class="detail-label">ISBN</span>
                <span class="detail-value">{{ book.isbn }}</span>
              </div>
              <div v-if="book.publisher" class="detail-field">
                <span class="detail-label">出版社</span>
                <span class="detail-value">{{ book.publisher }}</span>
              </div>
              <div v-if="book.publish_date" class="detail-field">
                <span class="detail-label">出版日期</span>
                <span class="detail-value">{{ formatDate(book.publish_date) }}</span>
              </div>
              <div v-if="book.category_name" class="detail-field">
                <span class="detail-label">分类</span>
                <span class="detail-value">{{ book.category_name }}</span>
              </div>
              <div v-if="book.language" class="detail-field">
                <span class="detail-label">语言</span>
                <span class="detail-value">{{ book.language }}</span>
              </div>
              <div v-if="book.price" class="detail-field">
                <span class="detail-label">定价</span>
                <span class="detail-value">{{ formatMoney(book.price) }}</span>
              </div>
            </div>
            
            <!-- CTA Buttons - Apple Pill Style -->
            <div class="flex flex-wrap gap-3">
              <button 
                class="px-5 py-2.5 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]"
                @click="handleReserve"
              >
                <el-icon class="mr-1"><Clock /></el-icon>
                {{ book.available_copies === 0 ? '预约此书（无库存）' : '预约此书' }}
              </button>
              <span v-if="book.available_copies > 0" class="inline-flex items-center text-[14px] text-white/48 tracking-[-0.224px] py-2.5">
                <el-icon class="mr-1"><InfoFilled /></el-icon>
                有 {{ book.available_copies }} 本可借，也可直接到图书馆借阅
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 简介 - Apple Light Section -->
      <div class="bg-apple-white rounded-large p-8 shadow-card">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-[28px] font-normal leading-[1.14] tracking-[0.196px] text-near-black">图书简介</h2>
          <button
            class="inline-flex items-center gap-1.5 px-4 py-2 bg-apple-blue text-white text-[13px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.12px] disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="aiLoading"
            @click="handleGenerateDescription"
          >
            <el-icon :class="{ 'animate-spin': aiLoading }"><component :is="aiLoading ? 'Loading' : 'MagicStick'" /></el-icon>
            {{ aiLoading ? '生成中...' : (book.description ? '重新生成' : 'AI 生成简介') }}
          </button>
        </div>
        <!-- 关键词输入 -->
        <div class="flex items-center gap-3 mb-5">
          <span class="text-[13px] text-text-tertiary tracking-[-0.12px] whitespace-nowrap">关注重点</span>
          <input
            v-model="aiKeywords"
            type="text"
            placeholder="如：写作手法、人物塑造、历史背景..."
            class="flex-1 h-9 px-3 bg-[#fafafc] rounded-standard border-[3px] border-[rgba(0,0,0,0.04)] text-[14px] text-near-black tracking-[-0.224px] outline-none focus:border-apple-blue/40 transition-colors placeholder:text-[rgba(0,0,0,0.32)]"
          />
        </div>
        <div v-if="aiLoading && !book.description" class="flex flex-col items-center justify-center py-12 gap-3">
          <el-icon size="32" class="animate-spin text-apple-blue"><Loading /></el-icon>
          <p class="text-[14px] text-text-tertiary tracking-[-0.224px]">AI 正在撰写简介，请稍候...</p>
        </div>
        <div v-else-if="book.description" class="description-content">
          {{ book.description }}
        </div>
        <div v-else class="flex flex-col items-center justify-center py-12 gap-3">
          <el-icon size="32" class="text-text-tertiary"><Document /></el-icon>
          <p class="text-[14px] text-text-tertiary tracking-[-0.224px]">暂无简介，填写关注重点后点击生成</p>
        </div>
      </div>
    </template>
    
    <el-empty v-else-if="!loading" description="图书不存在" />
  </div>
</template>

<style scoped>
.book-cover {
  width: 100%;
  aspect-ratio: 3/4;
  background: #1d1d1f;
  border-radius: 8px;
  overflow: hidden;
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
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.48);
  letter-spacing: -0.12px;
  line-height: 1.33;
}

.detail-value {
  font-size: 14px;
  color: #ffffff;
  letter-spacing: -0.224px;
  line-height: 1.29;
}

.description-content {
  line-height: 1.47;
  letter-spacing: -0.374px;
  color: rgba(0, 0, 0, 0.8);
  white-space: pre-wrap;
  font-size: 17px;
}
</style>
