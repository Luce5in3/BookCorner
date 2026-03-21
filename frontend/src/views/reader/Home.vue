<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getBooks, getCategoryTree } from '@/api/books'
import { getPublishedAnnouncements } from '@/api/announcements'
import { BOOK_STATUS } from '@/utils/format'

const router = useRouter()

const loading = ref(false)
const books = ref([])
const categories = ref([])
const announcements = ref([])

const searchParams = ref({
  search: '',
  category: '',
  page: 1,
  page_size: 12
})

const total = ref(0)

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
    books.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取图书失败:', error)
  } finally {
    loading.value = false
  }
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

onMounted(() => {
  fetchBooks()
  fetchCategories()
  fetchAnnouncements()
})
</script>

<template>
  <div class="home-container">
    <!-- 公告区域 -->
    <div v-if="announcements.length > 0" class="announcement-section">
      <el-carousel height="60px" direction="vertical" :autoplay="true" indicator-position="none">
        <el-carousel-item v-for="item in announcements" :key="item.id">
          <div class="announcement-item" @click="showAnnouncement(item)">
            <el-icon color="#E6A23C"><Bell /></el-icon>
            <span class="title">{{ item.title }}</span>
            <span class="view-detail">查看详情 &gt;</span>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
    
    <!-- 搜索区域 -->
    <div class="search-section">
      <el-row :gutter="20" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchParams.search"
            placeholder="搜索书名、作者..."
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-tree-select
            v-model="searchParams.category"
            :data="categories"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择分类"
            clearable
            check-strictly
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图书列表 -->
    <div v-loading="loading" class="book-section">
      <el-row :gutter="20">
        <el-col v-for="book in books" :key="book.id" :xs="12" :sm="8" :md="6" :lg="4" :xl="4">
          <el-card class="book-card" shadow="hover" @click="goToDetail(book.id)">
            <div class="book-cover">
              <el-image
                :src="book.cover_url || '/default-cover.png'"
                fit="cover"
                class="cover-img"
              >
                <template #error>
                  <div class="cover-placeholder">
                    <el-icon size="40"><Reading /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
            <div class="book-info">
              <h4 class="book-title" :title="book.title">{{ book.title }}</h4>
              <p class="book-author">{{ book.author }}</p>
              <div class="book-meta">
                <el-tag 
                  :type="book.available_copies > 0 ? 'success' : 'danger'" 
                  size="small"
                >
                  {{ book.available_copies > 0 ? `可借 ${book.available_copies}` : '暂无可借' }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
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
    <el-dialog v-model="announcementVisible" title="公告详情" width="500px">
      <div class="announcement-detail">
        <h3>{{ currentAnnouncement.title }}</h3>
        <el-divider />
        <p>{{ currentAnnouncement.content }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="announcementVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
}

.announcement-section {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.announcement-item {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 60px;
  cursor: pointer;
}

.announcement-item .title {
  flex: 1;
  color: #666;
  font-size: 14px;
}

.announcement-item .view-detail {
  color: #409EFF;
  font-size: 12px;
}

.search-section {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.book-section {
  min-height: 400px;
}

.book-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-cover {
  height: 180px;
  overflow: hidden;
  margin: -20px -20px 10px;
  background: #f5f7fa;
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
  background: #f5f7fa;
  color: #ccc;
}

.book-info {
  padding: 0 5px;
}

.book-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 12px;
  color: #999;
  margin: 0 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.announcement-detail h3 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #303133;
}

.announcement-detail p {
  margin: 0;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}
</style>
