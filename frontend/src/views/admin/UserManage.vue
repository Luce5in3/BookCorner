<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
import { USER_ROLE, USER_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const queryParams = ref({ search: '', role: '', status: '', page: 1, page_size: 10 })

async function fetchUsers() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (!params.search) delete params.search
    if (params.role === '') delete params.role
    if (params.status === '') delete params.status
    const data = await request.get('/api/users/', { params })
    users.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取用户失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() { queryParams.value.page = 1; fetchUsers() }
function handlePageChange(page) { queryParams.value.page = page; fetchUsers() }

async function handleToggleStatus(row) {
  try {
    const newStatus = row.status === 1 ? 0 : 1
    const action = newStatus === 0 ? '禁用' : '启用'
    await ElMessageBox.confirm(`确定要${action}用户 ${row.username} 吗？`, '操作确认', { type: 'warning' })
    await request.patch(`/api/users/${row.id}/`, { status: newStatus })
    ElMessage.success(`${action}成功`)
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') console.error('操作失败:', error)
  }
}

async function handleChangeRole(row, role) {
  try {
    await request.patch(`/api/users/${row.id}/`, { role })
    ElMessage.success('角色修改成功')
    fetchUsers()
  } catch (error) {
    console.error('修改角色失败:', error)
  }
}

onMounted(() => { fetchUsers() })
</script>

<template>
  <div>
    <!-- Search Bar -->
    <div class="bg-apple-white rounded-large shadow-card p-5 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="flex-1 min-w-[180px]">
          <el-input v-model="queryParams.search" placeholder="搜索用户名/姓名" clearable class="apple-input" @keyup.enter="handleSearch" />
        </div>
        <div class="w-[120px]">
          <el-select v-model="queryParams.role" placeholder="角色" clearable>
            <el-option v-for="(label, value) in USER_ROLE" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </div>
        <div class="w-[120px]">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in USER_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </div>
        <button class="h-[40px] px-4 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSearch">搜索</button>
      </div>
    </div>
    
    <!-- Table -->
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <div class="p-5">
        <el-table v-loading="loading" :data="users" class="apple-table">
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="real_name" label="真实姓名" width="120" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column prop="role" label="角色" width="120">
            <template #default="{ row }">
              <el-select v-model="row.role" size="small" @change="handleChangeRole(row, $event)">
                <el-option v-for="(label, value) in USER_ROLE" :key="value" :label="label" :value="Number(value)" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'user')" size="small" class="!border-none !rounded-pill !text-[12px]">{{ USER_STATUS[row.status] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <button v-if="row.status === 1" class="text-[14px] text-danger-red hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleToggleStatus(row)">禁用</button>
              <button v-else class="text-[14px] text-success-green hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleToggleStatus(row)">启用</button>
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
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
:deep(.apple-table) { --el-table-border-color: rgba(0, 0, 0, 0.06); --el-table-header-bg-color: #f5f5f7; }
:deep(.apple-table th.el-table__cell) { font-size: 12px !important; font-weight: 600 !important; color: rgba(0, 0, 0, 0.48) !important; letter-spacing: -0.12px !important; }
:deep(.apple-table td.el-table__cell) { font-size: 14px !important; letter-spacing: -0.224px !important; }
</style>
