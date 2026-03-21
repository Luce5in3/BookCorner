<script setup>
import { ref, onMounted } from 'vue'
import { getMyBorrows, renewBook } from '@/api/borrows'
import { formatDateTime, BORROW_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const borrows = ref([])
const total = ref(0)
const queryParams = ref({
  page: 1,
  page_size: 10
})

async function fetchBorrows() {
  loading.value = true
  try {
    const data = await getMyBorrows(queryParams.value)
    borrows.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取借阅记录失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleRenew(row) {
  try {
    await ElMessageBox.confirm(`确定要续借《${row.book_title}》吗？`, '续借确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await renewBook(row.id)
    ElMessage.success('续借成功')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('续借失败:', error)
    }
  }
}

function handlePageChange(page) {
  queryParams.value.page = page
  fetchBorrows()
}

// 判断是否可以续借
function canRenew(row) {
  // 只有借阅中状态才能续借
  return row.status === 1
}

// 判断是否逾期
function isOverdue(row) {
  if (row.status !== 1) return false
  return new Date(row.due_at) < new Date()
}

onMounted(() => {
  fetchBorrows()
})
</script>

<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的借阅</span>
        </div>
      </template>
      
      <el-table v-loading="loading" :data="borrows" stripe>
        <el-table-column prop="book_title" label="书名" min-width="200">
          <template #default="{ row }">
            <span class="book-title">{{ row.book_title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="book_copy_barcode" label="条码" width="120" />
        <el-table-column prop="borrow_at" label="借阅时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.borrow_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="due_at" label="应还时间" width="170">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row) }">
              {{ formatDateTime(row.due_at) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="return_at" label="归还时间" width="170">
          <template #default="{ row }">
            {{ row.return_at ? formatDateTime(row.return_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'borrow')">
              {{ BORROW_STATUS[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canRenew(row)"
              type="primary"
              link
              @click="handleRenew(row)"
            >
              续借
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

.text-danger {
  color: #F56C6C;
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
