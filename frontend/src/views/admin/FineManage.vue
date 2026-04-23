<script setup>
import { ref, onMounted } from 'vue'
import { getFines, waiveFine } from '@/api/fines'
import { formatDateTime, formatMoney, FINE_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const fines = ref([])
const total = ref(0)
const queryParams = ref({ status: '', page: 1, page_size: 10 })

async function fetchFines() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (params.status === '') delete params.status
    const data = await getFines(params)
    fines.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取罚款记录失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() { queryParams.value.page = 1; fetchFines() }
function handlePageChange(page) { queryParams.value.page = page; fetchFines() }

async function handleWaive(row) {
  try {
    await ElMessageBox.confirm(`确定要免除该笔 ${formatMoney(row.amount)} 的罚款吗？`, '免除确认', { type: 'warning' })
    await waiveFine(row.id)
    ElMessage.success('已免除')
    fetchFines()
  } catch (error) {
    if (error !== 'cancel') console.error('操作失败:', error)
  }
}

onMounted(() => { fetchFines() })
</script>

<template>
  <div>
    <!-- Search Bar -->
    <div class="bg-apple-white rounded-large shadow-card p-5 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="w-[140px]">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in FINE_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </div>
        <button class="h-[40px] px-4 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSearch">搜索</button>
      </div>
    </div>
    
    <!-- Table -->
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <div class="p-5">
        <el-table v-loading="loading" :data="fines" class="apple-table">
          <el-table-column prop="user_name" label="用户" width="100" />
          <el-table-column prop="book_title" label="相关图书" min-width="200">
            <template #default="{ row }">
              <span class="font-semibold text-near-black tracking-[-0.224px]">{{ row.book_title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" width="120" />
          <el-table-column prop="amount" label="金额" width="100">
            <template #default="{ row }">
              <span class="text-danger-red font-semibold tracking-[-0.224px]">{{ formatMoney(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="生成时间" width="170">
            <template #default="{ row }"><span class="text-text-secondary">{{ formatDateTime(row.created_at) }}</span></template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'fine')" size="small" class="!border-none !rounded-pill !text-[12px]">{{ FINE_STATUS[row.status] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <button v-if="row.status === 0" class="text-[14px] text-[#E6A23C] hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleWaive(row)">免除</button>
              <span v-else class="text-text-tertiary">-</span>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="total > 0" class="pagination-container">
          <el-pagination v-model:current-page="queryParams.page" :page-size="queryParams.page_size" :total="total" layout="prev, pager, next, total" @current-change="handlePageChange" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-danger-red { color: #FF3B30; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
:deep(.apple-table) { --el-table-border-color: rgba(0, 0, 0, 0.06); --el-table-header-bg-color: #f5f5f7; }
:deep(.apple-table th.el-table__cell) { font-size: 12px !important; font-weight: 600 !important; color: rgba(0, 0, 0, 0.48) !important; letter-spacing: -0.12px !important; }
:deep(.apple-table td.el-table__cell) { font-size: 14px !important; letter-spacing: -0.224px !important; }
</style>
