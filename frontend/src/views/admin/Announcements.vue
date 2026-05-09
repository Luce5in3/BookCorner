<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, publishAnnouncement, unpublishAnnouncement } from '@/api/announcements'
import { formatDateTime, ANNOUNCEMENT_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const announcements = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)

const queryParams = ref({ status: '', page: 1, page_size: 10 })

const form = reactive({ id: null, title: '', content: '' })

// 查看详情弹窗
const detailVisible = ref(false)
const detailData = ref({ title: '', content: '', admin_name: '', published_at: null })

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

async function fetchAnnouncements() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (params.status === '') delete params.status
    const data = await getAnnouncements(params)
    announcements.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取公告失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() { queryParams.value.page = 1; fetchAnnouncements() }
function handlePageChange(page) { queryParams.value.page = page; fetchAnnouncements() }

function handleAdd() {
  dialogTitle.value = '新增公告'
  Object.assign(form, { id: null, title: '', content: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑公告'
  Object.assign(form, { id: row.id, title: row.title, content: row.content })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    if (form.id) {
      await updateAnnouncement(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAnnouncements()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该公告吗？', '删除确认', { type: 'warning' })
    await deleteAnnouncement(row.id)
    ElMessage.success('删除成功')
    fetchAnnouncements()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

async function handlePublish(row) {
  try {
    await publishAnnouncement(row.id)
    ElMessage.success('发布成功')
    fetchAnnouncements()
  } catch (error) {
    console.error('发布失败:', error)
  }
}

async function handleUnpublish(row) {
  try {
    await unpublishAnnouncement(row.id)
    ElMessage.success('下架成功')
    fetchAnnouncements()
  } catch (error) {
    console.error('下架失败:', error)
  }
}

// 查看详情
function handleView(row) {
  detailData.value = {
    title: row.title,
    content: row.content,
    admin_name: row.admin_name,
    published_at: row.published_at
  }
  detailVisible.value = true
}

onMounted(() => { fetchAnnouncements() })
</script>

<template>
  <div>
    <!-- Search Bar -->
    <div class="bg-apple-white rounded-large shadow-card p-5 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="w-[140px]">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in ANNOUNCEMENT_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </div>
        <button class="h-[40px] px-4 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSearch">搜索</button>
        <button class="h-[40px] px-4 bg-near-black text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-85 transition-opacity tracking-[-0.224px]" @click="handleAdd">新增</button>
      </div>
    </div>
    
    <!-- Table -->
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <div class="p-5">
        <el-table v-loading="loading" :data="announcements" class="apple-table">
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <button class="text-[14px] text-link-blue hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer p-0" @click="handleView(row)">{{ row.title }}</button>
            </template>
          </el-table-column>
          <el-table-column prop="admin_name" label="发布者" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="170">
            <template #default="{ row }"><span class="text-text-secondary">{{ formatDateTime(row.created_at) }}</span></template>
          </el-table-column>
          <el-table-column prop="published_at" label="发布时间" width="170">
            <template #default="{ row }"><span class="text-text-secondary">{{ row.published_at ? formatDateTime(row.published_at) : '-' }}</span></template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'announcement')" size="small" class="!border-none !rounded-pill !text-[12px]">{{ ANNOUNCEMENT_STATUS[row.status] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <div class="flex gap-2 flex-wrap">
                <button class="text-[14px] text-text-tertiary hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleView(row)">查看</button>
                <button class="text-[14px] text-link-blue hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleEdit(row)">编辑</button>
                <button v-if="row.status === 0" class="text-[14px] text-success-green hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handlePublish(row)">发布</button>
                <button v-else-if="row.status === 1" class="text-[14px] text-[#E6A23C] hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleUnpublish(row)">下架</button>
                <button class="text-[14px] text-danger-red hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleDelete(row)">删除</button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="total > 0" class="pagination-container">
          <el-pagination v-model:current-page="queryParams.page" :page-size="queryParams.page_size" :total="total" layout="prev, pager, next, total" @current-change="handlePageChange" />
        </div>
      </div>
    </div>
    
    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" class="apple-form">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="px-4 py-2 text-[14px] text-text-secondary rounded-standard border border-[rgba(0,0,0,0.1)] bg-transparent cursor-pointer hover:bg-apple-gray transition-colors tracking-[-0.224px] mr-2" @click="dialogVisible = false">取消</button>
        <button class="px-4 py-2 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSubmit">确定</button>
      </template>
    </el-dialog>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="detailVisible" title="公告详情" width="600px">
      <div class="detail-content">
        <h3 class="detail-title">{{ detailData.title }}</h3>
        <div class="detail-meta">
          <span class="text-[12px] text-text-tertiary tracking-[-0.12px]">发布者：{{ detailData.admin_name || '-' }}</span>
          <span v-if="detailData.published_at" class="text-[12px] text-text-tertiary tracking-[-0.12px]">发布时间：{{ formatDateTime(detailData.published_at) }}</span>
        </div>
        <div class="h-px bg-[rgba(0,0,0,0.1)] my-4"></div>
        <div class="detail-body">{{ detailData.content }}</div>
      </div>
      <template #footer>
        <button class="px-4 py-2 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="detailVisible = false">关闭</button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.detail-content { padding: 8px 0; }
.detail-title { margin: 0 0 12px; font-size: 21px; font-weight: 600; color: #1d1d1f; letter-spacing: 0.231px; line-height: 1.19; }
.detail-meta { color: rgba(0, 0, 0, 0.48); font-size: 12px; display: flex; gap: 16px; }
.detail-body { white-space: pre-wrap; line-height: 1.47; letter-spacing: -0.374px; color: rgba(0, 0, 0, 0.8); font-size: 17px; }

:deep(.apple-table) { --el-table-border-color: rgba(0, 0, 0, 0.06); --el-table-header-bg-color: #f5f5f7; }
:deep(.apple-table th.el-table__cell) { font-size: 12px !important; font-weight: 600 !important; color: rgba(0, 0, 0, 0.48) !important; letter-spacing: -0.12px !important; }
:deep(.apple-table td.el-table__cell) { font-size: 14px !important; letter-spacing: -0.224px !important; }
.apple-form :deep(.el-form-item__label) { font-size: 14px !important; font-weight: 600 !important; color: #1d1d1f !important; letter-spacing: -0.224px !important; }
</style>
