<script setup>
import { ref, onMounted } from 'vue'
import { getBorrows, returnBook, markLost, borrowBook } from '@/api/borrows'
import { searchReaders } from '@/api/users'
import { formatDateTime, BORROW_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const borrows = ref([])
const total = ref(0)
const queryParams = ref({ status: '', page: 1, page_size: 10 })

// 办理借阅对话框
const borrowDialogVisible = ref(false)
const borrowForm = ref({
  user_id: null,
  barcode: '',
  days: 30
})
const borrowFormRef = ref(null)
const userOptions = ref([])
const userLoading = ref(false)
const borrowSubmitting = ref(false)

const borrowRules = {
  user_id: [{ required: true, message: '请选择读者', trigger: 'change' }],
  barcode: [{ required: true, message: '请输入副本条码', trigger: 'blur' }]
}

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

// 打开办理借阅对话框
function openBorrowDialog() {
  borrowForm.value = { user_id: null, barcode: '', days: 30 }
  userOptions.value = []
  borrowDialogVisible.value = true
}

// 搜索读者
async function handleSearchUser(query) {
  if (!query || query.length < 1) {
    userOptions.value = []
    return
  }
  userLoading.value = true
  try {
    const data = await searchReaders(query)
    userOptions.value = (data.results || []).map(u => ({
      value: u.id,
      label: `${u.username} - ${u.real_name || '未设置姓名'}${u.phone ? ' (' + u.phone + ')' : ''}`
    }))
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    userLoading.value = false
  }
}

// 提交借阅
async function submitBorrow() {
  try {
    await borrowFormRef.value.validate()
  } catch {
    return
  }
  
  borrowSubmitting.value = true
  try {
    await borrowBook({
      user_id: borrowForm.value.user_id,
      barcode: borrowForm.value.barcode,
      days: borrowForm.value.days
    })
    ElMessage.success('借阅成功')
    borrowDialogVisible.value = false
    fetchBorrows()
  } catch (error) {
    console.error('借阅失败:', error)
  } finally {
    borrowSubmitting.value = false
  }
}

onMounted(() => { fetchBorrows() })
</script>

<template>
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20" align="middle">
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in BORROW_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
        </el-col>
        <el-col :span="16" style="text-align: right;">
          <el-button type="success" icon="Plus" @click="openBorrowDialog">办理借阅</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="borrows" stripe :row-class-name="({ row }) => isOverdue(row) ? 'overdue-row' : ''">
        <el-table-column prop="real_name" label="用户" width="100">
          <template #default="{ row }">{{ row.real_name || row.username }}</template>
        </el-table-column>
        <el-table-column prop="book_title" label="图书" min-width="200" />
        <el-table-column prop="barcode" label="条码" width="120" />
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
    
    <!-- 办理借阅对话框 -->
    <el-dialog v-model="borrowDialogVisible" title="办理借阅" width="500px">
      <el-form ref="borrowFormRef" :model="borrowForm" :rules="borrowRules" label-width="100px">
        <el-form-item label="读者" prop="user_id">
          <el-select
            v-model="borrowForm.user_id"
            filterable
            remote
            reserve-keyword
            placeholder="输入用户名/姓名/手机号搜索"
            :remote-method="handleSearchUser"
            :loading="userLoading"
            style="width: 100%;"
          >
            <el-option v-for="item in userOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="副本条码" prop="barcode">
          <el-input v-model="borrowForm.barcode" placeholder="扫描或输入副本条码" />
        </el-form-item>
        <el-form-item label="借阅天数">
          <el-input-number v-model="borrowForm.days" :min="1" :max="90" />
          <span class="ml-10 text-muted">天</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="borrowSubmitting" @click="submitBorrow">确定借出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-bar { background: #fff; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.table-container { background: #fff; padding: 20px; border-radius: 4px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.text-danger { color: #F56C6C; }
.text-muted { color: #909399; }
.ml-10 { margin-left: 10px; }
:deep(.overdue-row) { background-color: #fef0f0 !important; }
</style>
