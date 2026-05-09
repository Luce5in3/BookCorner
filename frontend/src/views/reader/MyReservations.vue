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
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-[rgba(0,0,0,0.06)]">
        <h2 class="text-[28px] font-normal leading-[1.14] tracking-[0.196px] text-near-black">我的预约</h2>
      </div>
      
      <div class="p-6">
        <el-table v-loading="loading" :data="reservations" class="apple-table">
          <el-table-column prop="book_title" label="书名" min-width="200">
            <template #default="{ row }">
              <span class="font-semibold text-near-black tracking-[-0.224px]">{{ row.book_title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="reserved_at" label="预约时间" width="170">
            <template #default="{ row }">
              <span class="text-text-secondary">{{ formatDateTime(row.reserved_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="expire_at" label="过期时间" width="170">
            <template #default="{ row }">
              <span class="text-text-secondary">{{ formatDateTime(row.expire_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="notify_at" label="通知时间" width="170">
            <template #default="{ row }">
              <span class="text-text-secondary">{{ row.notify_at ? formatDateTime(row.notify_at) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'reservation')" size="small" class="!border-none !rounded-pill !text-[12px]">
                {{ RESERVATION_STATUS[row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <button
                v-if="canCancel(row)"
                class="text-[14px] text-danger-red hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer"
                @click="handleCancel(row)"
              >
                取消
              </button>
              <span v-else class="text-text-tertiary">-</span>
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
      </div>
    </div>
  </div>
</template>

<style scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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
