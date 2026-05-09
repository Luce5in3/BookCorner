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
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-[rgba(0,0,0,0.06)]">
        <h2 class="text-[28px] font-normal leading-[1.14] tracking-[0.196px] text-near-black">我的罚款</h2>
      </div>
      
      <div class="p-6">
        <el-table v-loading="loading" :data="fines" class="apple-table">
          <el-table-column prop="book_title" label="相关图书" min-width="200">
            <template #default="{ row }">
              <span class="font-semibold text-near-black tracking-[-0.224px]">{{ row.book_title || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" width="150" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              <span class="text-danger-red font-semibold tracking-[-0.224px]">{{ formatMoney(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="生成时间" width="170">
            <template #default="{ row }">
              <span class="text-text-secondary">{{ formatDateTime(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="paid_at" label="缴纳时间" width="170">
            <template #default="{ row }">
              <span class="text-text-secondary">{{ row.paid_at ? formatDateTime(row.paid_at) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'fine')" size="small" class="!border-none !rounded-pill !text-[12px]">
                {{ FINE_STATUS[row.status] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <button
                v-if="canPay(row)"
                class="text-[14px] text-link-blue hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer"
                @click="handlePay(row)"
              >
                缴纳
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
.text-danger-red {
  color: #FF3B30;
}

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
