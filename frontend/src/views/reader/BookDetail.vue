<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getBook } from '@/api/books'
import { createReservation } from '@/api/reservations'
import { formatDate, formatMoney, BOOK_STATUS } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const book = ref(null)

async function fetchBook() {
  loading.value = true
  try {
    const data = await getBook(route.params.id)
    book.value = data
  } catch (error) {
    console.error('获取图书详情失败:', error)
  } finally {
    loading.value = false
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

onMounted(() => {
  fetchBook()
})
</script>

<template>
  <div v-loading="loading" class="detail-container">
    <template v-if="book">
      <el-card class="book-detail-card">
        <el-row :gutter="40">
          <!-- 封面 -->
          <el-col :span="6">
            <div class="book-cover">
              <el-image
                :src="book.cover_url || '/default-cover.png'"
                fit="cover"
                class="cover-img"
              >
                <template #error>
                  <div class="cover-placeholder">
                    <el-icon size="80"><Reading /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </el-col>
          
          <!-- 详情 -->
          <el-col :span="18">
            <div class="book-info">
              <h1 class="book-title">{{ book.title }}</h1>
              
              <div class="book-meta">
                <el-tag :type="book.status === 1 ? 'success' : 'info'" size="large">
                  {{ BOOK_STATUS[book.status] }}
                </el-tag>
                <el-tag 
                  :type="book.available_copies > 0 ? 'success' : 'danger'" 
                  size="large"
                >
                  可借 {{ book.available_copies }} / 总 {{ book.total_copies }}
                </el-tag>
              </div>
              
              <el-descriptions :column="2" border class="info-table">
                <el-descriptions-item label="作者">{{ book.author }}</el-descriptions-item>
                <el-descriptions-item label="ISBN">{{ book.isbn || '-' }}</el-descriptions-item>
                <el-descriptions-item label="出版社">{{ book.publisher || '-' }}</el-descriptions-item>
                <el-descriptions-item label="出版日期">{{ formatDate(book.publish_date) }}</el-descriptions-item>
                <el-descriptions-item label="分类">{{ book.category_name || '-' }}</el-descriptions-item>
                <el-descriptions-item label="语言">{{ book.language || '-' }}</el-descriptions-item>
                <el-descriptions-item label="定价">{{ formatMoney(book.price) }}</el-descriptions-item>
              </el-descriptions>
              
              <div class="action-buttons">
                <el-button 
                  v-if="book.available_copies === 0"
                  type="primary" 
                  size="large"
                  icon="Clock"
                  @click="handleReserve"
                >
                  预约此书
                </el-button>
                <el-text v-if="book.available_copies > 0" type="success">
                  <el-icon><InfoFilled /></el-icon>
                  有 {{ book.available_copies }} 本可借，请到图书馆借阅
                </el-text>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 简介 -->
      <el-card v-if="book.description" class="description-card">
        <template #header>
          <span>图书简介</span>
        </template>
        <div class="description-content">
          {{ book.description }}
        </div>
      </el-card>
    </template>
    
    <el-empty v-else-if="!loading" description="图书不存在" />
  </div>
</template>

<style scoped>
.detail-container {
  padding: 20px;
}

.book-detail-card {
  margin-bottom: 20px;
}

.book-cover {
  width: 100%;
  aspect-ratio: 3/4;
  background: #f5f7fa;
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
  color: #ccc;
}

.book-info {
  padding: 20px 0;
}

.book-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px;
}

.book-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.info-table {
  margin-bottom: 30px;
}

.action-buttons {
  margin-top: 20px;
}

.description-card {
  margin-bottom: 20px;
}

.description-content {
  line-height: 1.8;
  color: #666;
  white-space: pre-wrap;
}
</style>
