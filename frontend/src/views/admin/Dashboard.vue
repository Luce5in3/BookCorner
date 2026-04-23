<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats, getDashboardRecent } from '@/api/dashboard'
import { Reading, User, Tickets, Clock } from '@element-plus/icons-vue'
import { Bell } from '@element-plus/icons-vue'

const loading = ref(false)

// 统计数据
const stats = ref({
  total_books: 0,
  total_users: 0,
  active_borrows: 0,
  pending_reservations: 0
})

// 最近数据
const recentBorrows = ref([])
const recentAnnouncements = ref([])

// 公告详情弹窗
const announcementVisible = ref(false)
const currentAnnouncement = ref({ title: '', content: '' })

// 统计卡片配置 - Apple Dark Surface
const statCards = [
  { key: 'total_books', label: '图书总数', icon: Reading },
  { key: 'total_users', label: '读者总数', icon: User },
  { key: 'active_borrows', label: '借阅中', icon: Tickets },
  { key: 'pending_reservations', label: '预约中', icon: Clock },
]

async function fetchStats() {
  try {
    const data = await getDashboardStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

async function fetchRecent() {
  try {
    const data = await getDashboardRecent()
    recentBorrows.value = data.recent_borrows || []
    recentAnnouncements.value = data.recent_announcements || []
  } catch (error) {
    console.error('获取最近数据失败:', error)
  }
}

function getStatusType(status) {
  const types = { 0: 'info', 1: 'success', 2: 'warning', 3: 'danger' }
  return types[status] || 'info'
}

function showAnnouncement(item) {
  currentAnnouncement.value = { title: item.title, content: item.content }
  announcementVisible.value = true
}

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchStats(), fetchRecent()])
  loading.value = false
})
</script>

<template>
  <div class="dashboard-container" v-loading="loading">
    <!-- Hero Stats - Apple Light Section -->
    <div class="bg-apple-white rounded-large p-8 shadow-card mb-6">
      <h2 class="text-[40px] font-semibold text-near-black leading-[1.10] mb-6">数据总览</h2>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="card in statCards" :key="card.key" class="bg-apple-gray rounded-standard p-5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-standard bg-apple-blue/10 flex items-center justify-center">
              <el-icon :size="20" color="#0071e3"><component :is="card.icon" /></el-icon>
            </div>
          </div>
          <div class="text-[28px] font-semibold text-near-black leading-[1.14] tracking-[0.196px]">{{ stats[card.key] }}</div>
          <div class="text-[14px] text-text-secondary mt-1 tracking-[-0.224px]">{{ card.label }}</div>
        </div>
      </div>
    </div>

    <!-- 数据列表区域 - Apple Light Section -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div class="lg:col-span-3 bg-apple-white rounded-large shadow-card overflow-hidden">
        <div class="px-6 py-4 border-b border-[rgba(0,0,0,0.06)]">
          <h3 class="text-[21px] font-semibold text-near-black leading-[1.19] tracking-[0.231px]">最近借阅记录</h3>
        </div>
        <div class="p-6">
          <el-table :data="recentBorrows" size="small" max-height="400" class="apple-table">
            <el-table-column prop="user_name" label="读者" width="120" />
            <el-table-column prop="book_title" label="图书" min-width="200" show-overflow-tooltip />
            <el-table-column prop="borrow_date" label="借阅日期" width="120" />
            <el-table-column prop="status_display" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small" class="!border-none !rounded-pill !text-[12px]">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentBorrows.length === 0" description="暂无借阅记录" />
        </div>
      </div>
      <div class="lg:col-span-2 bg-apple-white rounded-large shadow-card overflow-hidden">
        <div class="px-6 py-4 border-b border-[rgba(0,0,0,0.06)]">
          <h3 class="text-[21px] font-semibold text-near-black leading-[1.19] tracking-[0.231px]">最新公告</h3>
        </div>
        <div class="p-4">
          <div class="announcement-list">
            <div v-for="item in recentAnnouncements" :key="item.id" class="announcement-item" @click="showAnnouncement(item)">
              <el-icon class="announcement-icon" color="#0071e3" size="14"><Bell /></el-icon>
              <span class="announcement-title">{{ item.title }}</span>
              <span class="announcement-date">{{ item.created_at }}</span>
            </div>
            <el-empty v-if="recentAnnouncements.length === 0" description="暂无公告" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 公告详情弹窗 -->
    <el-dialog v-model="announcementVisible" title="公告详情" width="500px">
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
  </div>
</template>

<style scoped>
.dashboard-container {
  min-height: calc(100vh - 120px);
}

.announcement-list {
  max-height: 400px;
  overflow-y: auto;
}

.announcement-item {
  display: flex;
  align-items: center;
  padding: 10px 8px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  gap: 8px;
  cursor: pointer;
  transition: background 200ms ease;
  border-radius: 5px;
}

.announcement-item:hover {
  background: #f5f5f7;
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-icon {
  flex-shrink: 0;
}

.announcement-title {
  flex: 1;
  font-size: 14px;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.224px;
}

.announcement-date {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.48);
  flex-shrink: 0;
  letter-spacing: -0.12px;
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

/* Apple Table Overrides */
:deep(.apple-table) {
  --el-table-border-color: rgba(0, 0, 0, 0.06);
  --el-table-header-bg-color: #f5f5f7;
}

:deep(.apple-table th.el-table__cell) {
  font-size: 12px !important;
  font-weight: 600 !important;
  color: rgba(0, 0, 0, 0.48) !important;
  letter-spacing: -0.12px !important;
}

:deep(.apple-table td.el-table__cell) {
  font-size: 14px !important;
  letter-spacing: -0.224px !important;
}
</style>
