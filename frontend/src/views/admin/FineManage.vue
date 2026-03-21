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
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in FINE_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="fines" stripe>
        <el-table-column prop="user_name" label="用户" width="100" />
        <el-table-column prop="book_title" label="相关图书" min-width="200" />
        <el-table-column prop="reason" label="原因" width="120" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span class="amount">{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'fine')">{{ FINE_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 0" type="warning" link @click="handleWaive(row)">免除</el-button>
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
.amount { color: #F56C6C; font-weight: 600; }
.text-muted { color: #c0c4cc; }
</style>
