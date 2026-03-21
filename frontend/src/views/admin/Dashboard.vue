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

// 统计卡片配置
const statCards = [
  { key: 'total_books', label: '图书总数', icon: Reading, color: 'blue' },
  { key: 'total_users', label: '读者总数', icon: User, color: 'green' },
  { key: 'active_borrows', label: '借阅中', icon: Tickets, color: 'orange' },
  { key: 'pending_reservations', label: '预约中', icon: Clock, color: 'purple' },
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
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="stat-card" :class="card.color">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="32"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats[card.key] }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据列表区域 -->
    <el-row :gutter="20" class="data-row">
      <el-col :xs="24" :lg="16">
        <el-card shadow="hover">
          <template #header>
            <span>最近借阅记录</span>
          </template>
          <el-table :data="recentBorrows" stripe size="small" max-height="400">
            <el-table-column prop="user_name" label="读者" width="120" />
            <el-table-column prop="book_title" label="图书" min-width="200" show-overflow-tooltip />
            <el-table-column prop="borrow_date" label="借阅日期" width="120" />
            <el-table-column prop="status_display" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentBorrows.length === 0" description="暂无借阅记录" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="hover">
          <template #header>
            <span>最新公告</span>
          </template>
          <div class="announcement-list">
            <div v-for="item in recentAnnouncements" :key="item.id" class="announcement-item" @click="showAnnouncement(item)">
              <el-icon class="announcement-icon"><Bell /></el-icon>
              <span class="announcement-title">{{ item.title }}</span>
              <span class="announcement-date">{{ item.created_at }}</span>
            </div>
            <el-empty v-if="recentAnnouncements.length === 0" description="暂无公告" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
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
.dashboard-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-card.blue .stat-icon { background: linear-gradient(135deg, #409EFF, #66b1ff); }
.stat-card.green .stat-icon { background: linear-gradient(135deg, #67C23A, #85ce61); }
.stat-card.orange .stat-icon { background: linear-gradient(135deg, #E6A23C, #ebb563); }
.stat-card.purple .stat-icon { background: linear-gradient(135deg, #9c27b0, #ba68c8); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.data-row .el-col {
  margin-bottom: 20px;
}

.announcement-list {
  max-height: 400px;
  overflow-y: auto;
}

.announcement-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
  gap: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.announcement-item:hover {
  background: #f5f7fa;
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-icon {
  color: #E6A23C;
  flex-shrink: 0;
}

.announcement-title {
  flex: 1;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.announcement-date {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
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
