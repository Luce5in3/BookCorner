<script setup>
import { ref, onMounted } from 'vue'
import { getMyReservations, cancelReservation } from '@/api/reservations'
import { formatDateTime, RESERVATION_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const reservations = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  page_size: 10
})

async function fetchReservations() {
  loading.value = true
  try {
    const data = await getMyReservations(queryParams.value)
    reservations.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取预约记录失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm(`确定要取消《${row.book_title}》的预约吗？`, '取消预约', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await cancelReservation(row.id)
    ElMessage.success('已取消预约')
    fetchReservations()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消预约失败:', error)
    }
  }
}

function handlePageChange(page) {
  queryParams.value.page = page
  fetchReservations()
}

// 判断是否可以取消
function canCancel(row) {
  // 只有预约中状态才能取消
  return row.status === 1
}

onMounted(() => {
  fetchReservations()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的预约</span>
        </div>
      </template>
      
      <el-table v-loading="loading" :data="reservations" stripe>
        <el-table-column prop="book_title" label="书名" min-width="200">
          <template #default="{ row }">
            <span class="book-title">{{ row.book_title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reserved_at" label="预约时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.reserved_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="expire_at" label="过期时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.expire_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="notify_at" label="通知时间" width="170">
          <template #default="{ row }">
            {{ row.notify_at ? formatDateTime(row.notify_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'reservation')">
              {{ RESERVATION_STATUS[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canCancel(row)"
              type="danger"
              link
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          :page-size="queryParams.page_size"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-title {
  font-weight: 500;
}

.text-muted {
  color: #c0c4cc;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
