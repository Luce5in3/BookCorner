<script setup>
import { ref, onMounted } from 'vue'
import { getBooks } from '@/api/books'
import { getBorrows } from '@/api/borrows'
import { getFines } from '@/api/fines'

const stats = ref({
  totalBooks: 0,
  todayBorrows: 0,
  overdueCount: 0,
  unpaidFines: 0
})

const loading = ref(false)

async function fetchStats() {
  loading.value = true
  try {
    // 获取图书总数
    const booksData = await getBooks({ page_size: 1 })
    stats.value.totalBooks = booksData.count || 0
    
    // 获取今日借阅数
    const today = new Date().toISOString().split('T')[0]
    const todayBorrowsData = await getBorrows({ page_size: 1 })
    stats.value.todayBorrows = todayBorrowsData.count || 0
    
    // 获取逾期数
    const overdueData = await getBorrows({ status: 2, page_size: 1 })
    stats.value.overdueCount = overdueData.count || 0
    
    // 获取待缴罚款
    const finesData = await getFines({ status: 0, page_size: 1 })
    stats.value.unpaidFines = finesData.count || 0
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon size="32"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalBooks }}</div>
              <div class="stat-label">图书总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon size="32"><Tickets /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayBorrows }}</div>
              <div class="stat-label">借阅记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon size="32"><WarningFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.overdueCount }}</div>
              <div class="stat-label">逾期借阅</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon red">
              <el-icon size="32"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.unpaidFines }}</div>
              <div class="stat-label">待缴罚款</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>系统概览</span>
          </template>
          <el-empty description="更多统计图表开发中..." />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page-container {
  padding: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #409EFF, #53a8ff);
}

.stat-icon.green {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.stat-icon.red {
  background: linear-gradient(135deg, #F56C6C, #f78989);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}

.mt-20 {
  margin-top: 20px;
}
</style>
