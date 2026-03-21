<script setup>
import { ref, onMounted } from 'vue'
import { getBorrows, returnBook, markLost } from '@/api/borrows'
import { formatDateTime, BORROW_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const borrows = ref([])
const total = ref(0)
const queryParams = ref({ status: '', page: 1, page_size: 10 })

async function fetchBorrows() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (params.status === '') delete params.status
    const data = await getBorrows(params)
    borrows.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取借阅记录失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() { queryParams.value.page = 1; fetchBorrows() }
function handlePageChange(page) { queryParams.value.page = page; fetchBorrows() }

async function handleReturn(row) {
  try {
    await ElMessageBox.confirm(`确定办理《${row.book_title}》归还吗？`, '归还确认', { type: 'info' })
    await returnBook(row.id)
    ElMessage.success('归还成功')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') console.error('归还失败:', error)
  }
}

async function handleLost(row) {
  try {
    await ElMessageBox.confirm(`确定将《${row.book_title}》标记为丢失吗？`, '丢失确认', { type: 'warning' })
    await markLost(row.id)
    ElMessage.success('已标记丢失')
    fetchBorrows()
  } catch (error) {
    if (error !== 'cancel') console.error('操作失败:', error)
  }
}

function isOverdue(row) {
  return row.status === 1 && new Date(row.due_at) < new Date()
}

onMounted(() => { fetchBorrows() })
</script>

<template>
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in BORROW_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="borrows" stripe :row-class-name="({ row }) => isOverdue(row) ? 'overdue-row' : ''">
        <el-table-column prop="user_name" label="用户" width="100" />
        <el-table-column prop="book_title" label="图书" min-width="200" />
        <el-table-column prop="book_copy_barcode" label="条码" width="120" />
        <el-table-column prop="borrow_at" label="借阅时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.borrow_at) }}</template>
        </el-table-column>
        <el-table-column prop="due_at" label="应还时间" width="170">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row) }">{{ formatDateTime(row.due_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'borrow')">{{ BORROW_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 1 || row.status === 2">
              <el-button type="success" link @click="handleReturn(row)">归还</el-button>
              <el-button type="danger" link @click="handleLost(row)">丢失</el-button>
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="total > 0" class="pagination-container">
        <el-pagination v-model:current-page="queryParams.page" :page-size="queryParams.page_size" :total="total" layout="prev, pager, next, total" @current-change="handlePageChange" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-bar { background: #fff; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.table-container { background: #fff; padding: 20px; border-radius: 4px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.text-danger { color: #F56C6C; }
.text-muted { color: #c0c4cc; }
:deep(.overdue-row) { background-color: #fef0f0 !important; }
</style>
