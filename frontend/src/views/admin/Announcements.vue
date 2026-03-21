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
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in ANNOUNCEMENT_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
          <el-button type="success" icon="Plus" @click="handleAdd">新增</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="announcements" stripe>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="handleView(row)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="admin_name" label="发布者" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="170">
          <template #default="{ row }">{{ row.published_at ? formatDateTime(row.published_at) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'announcement')">{{ ANNOUNCEMENT_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="info" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 0" type="success" link @click="handlePublish(row)">发布</el-button>
            <el-button v-else-if="row.status === 1" type="warning" link @click="handleUnpublish(row)">下架</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="total > 0" class="pagination-container">
        <el-pagination v-model:current-page="queryParams.page" :page-size="queryParams.page_size" :total="total" layout="prev, pager, next, total" @current-change="handlePageChange" />
      </div>
    </div>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="6" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情弹窗 -->
    <el-dialog v-model="detailVisible" title="公告详情" width="600px">
      <div class="detail-content">
        <h3 class="detail-title">{{ detailData.title }}</h3>
        <div class="detail-meta">
          <span>发布者：{{ detailData.admin_name || '-' }}</span>
          <span v-if="detailData.published_at">发布时间：{{ formatDateTime(detailData.published_at) }}</span>
        </div>
        <el-divider />
        <div class="detail-body">{{ detailData.content }}</div>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-bar { background: #fff; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.table-container { background: #fff; padding: 20px; border-radius: 4px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.detail-content { padding: 10px 0; }
.detail-title { margin: 0 0 15px; font-size: 18px; color: #333; }
.detail-meta { color: #909399; font-size: 13px; display: flex; gap: 20px; }
.detail-body { white-space: pre-wrap; line-height: 1.8; color: #666; }
</style>
