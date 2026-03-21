<script setup>
import { ref, onMounted } from 'vue'
import { getMyFines, payFine } from '@/api/fines'
import { formatDateTime, formatMoney, FINE_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const fines = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  page_size: 10
})

async function fetchFines() {
  loading.value = true
  try {
    const data = await getMyFines(queryParams.value)
    fines.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取罚款记录失败:', error)
  } finally {
    loading.value = false
  }
}

async function handlePay(row) {
  try {
    await ElMessageBox.confirm(`确定缴纳罚款 ${formatMoney(row.amount)} 吗？`, '缴纳罚款', {
      confirmButtonText: '确定缴纳',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await payFine(row.id)
    ElMessage.success('缴纳成功')
    fetchFines()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('缴纳失败:', error)
    }
  }
}

function handlePageChange(page) {
  queryParams.value.page = page
  fetchFines()
}

// 判断是否可以缴纳
function canPay(row) {
  // 只有待缴状态才能缴纳
  return row.status === 0
}

onMounted(() => {
  fetchFines()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的罚款</span>
        </div>
      </template>
      
      <el-table v-loading="loading" :data="fines" stripe>
        <el-table-column prop="book_title" label="相关图书" min-width="200">
          <template #default="{ row }">
            <span class="book-title">{{ row.book_title || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="原因" width="150" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span class="amount">{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="缴纳时间" width="170">
          <template #default="{ row }">
            {{ row.paid_at ? formatDateTime(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'fine')">
              {{ FINE_STATUS[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canPay(row)"
              type="primary"
              link
              @click="handlePay(row)"
            >
              缴纳
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

.amount {
  color: #F56C6C;
  font-weight: 600;
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
