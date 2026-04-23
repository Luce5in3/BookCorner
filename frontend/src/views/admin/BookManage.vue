<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getBooks, createBook, updateBook, deleteBook, publishBook, unpublishBook, getCategoryTree } from '@/api/books'
import { formatDateTime, BOOK_STATUS, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const books = ref([])
const categories = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)

const queryParams = ref({
  search: '',
  category: '',
  status: '',
  page: 1,
  page_size: 10
})

const form = reactive({
  id: null,
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  cover_url: '',
  description: '',
  category_id: null,
  price: null,
  publish_date: '',
  language: 'zh'
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }]
}

async function fetchBooks() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (!params.search) delete params.search
    if (!params.category) delete params.category
    if (params.status === '') delete params.status
    
    const data = await getBooks(params)
    books.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取图书失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const data = await getCategoryTree()
    categories.value = data || []
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

function handleSearch() {
  queryParams.value.page = 1
  fetchBooks()
}

function handlePageChange(page) {
  queryParams.value.page = page
  fetchBooks()
}

function handleAdd() {
  dialogTitle.value = '新增图书'
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑图书'
  Object.assign(form, {
    id: row.id,
    isbn: row.isbn || '',
    title: row.title,
    author: row.author,
    publisher: row.publisher || '',
    cover_url: row.cover_url || '',
    description: row.description || '',
    category_id: row.category_id,
    price: row.price,
    publish_date: row.publish_date || '',
    language: row.language || 'zh'
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    
    const data = { ...form }
    if (!data.isbn) delete data.isbn
    if (!data.category_id) delete data.category_id
    
    if (form.id) {
      await updateBook(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await createBook(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    fetchBooks()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除《${row.title}》吗？`, '删除确认', {
      type: 'warning'
    })
    await deleteBook(row.id)
    ElMessage.success('删除成功')
    fetchBooks()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

async function handlePublish(row) {
  try {
    await publishBook(row.id)
    ElMessage.success('上架成功')
    fetchBooks()
  } catch (error) {
    console.error('上架失败:', error)
  }
}

async function handleUnpublish(row) {
  try {
    await unpublishBook(row.id)
    ElMessage.success('下架成功')
    fetchBooks()
  } catch (error) {
    console.error('下架失败:', error)
  }
}

function resetForm() {
  Object.assign(form, {
    id: null, isbn: '', title: '', author: '', publisher: '',
    cover_url: '', description: '', category_id: null,
    price: null, publish_date: '', language: 'zh'
  })
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
})
</script>

<template>
  <div>
    <!-- Search Bar - Apple Filter Style -->
    <div class="bg-apple-white rounded-large shadow-card p-5 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="flex-1 min-w-[180px]">
          <el-input v-model="queryParams.search" placeholder="搜索书名/作者" clearable class="apple-input" @keyup.enter="handleSearch" />
        </div>
        <div class="w-[160px]">
          <el-tree-select v-model="queryParams.category" :data="categories" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择分类" clearable check-strictly />
        </div>
        <div class="w-[100px]">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option label="上架" :value="1" />
            <el-option label="下架" :value="0" />
          </el-select>
        </div>
        <button class="h-[40px] px-4 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSearch">搜索</button>
        <button class="h-[40px] px-4 bg-near-black text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-85 transition-opacity tracking-[-0.224px]" @click="handleAdd">新增</button>
      </div>
    </div>
    
    <!-- Table -->
    <div class="bg-apple-white rounded-large shadow-card overflow-hidden">
      <div class="p-5">
        <el-table v-loading="loading" :data="books" class="apple-table">
          <el-table-column prop="title" label="书名" min-width="200">
            <template #default="{ row }">
              <span class="font-semibold text-near-black tracking-[-0.224px]">{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="author" label="作者" width="150" />
          <el-table-column prop="isbn" label="ISBN" width="150" />
          <el-table-column prop="category_name" label="分类" width="100" />
          <el-table-column label="库存" width="100">
            <template #default="{ row }">
              {{ row.available_copies }} / {{ row.total_copies }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status, 'book')" size="small" class="!border-none !rounded-pill !text-[12px]">{{ BOOK_STATUS[row.status] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="flex gap-2">
                <button class="text-[14px] text-link-blue hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleEdit(row)">编辑</button>
                <button v-if="row.status === 0" class="text-[14px] text-success-green hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handlePublish(row)">上架</button>
                <button v-else class="text-[14px] text-[#E6A23C] hover:underline tracking-[-0.224px] bg-transparent border-none cursor-pointer" @click="handleUnpublish(row)">下架</button>
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
    
    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px" class="apple-form">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input v-model="form.title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input v-model="form.author" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="ISBN">
              <el-input v-model="form.isbn" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-tree-select v-model="form.category_id" :data="categories" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择分类" clearable check-strictly style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="出版社">
              <el-input v-model="form.publisher" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出版日期">
              <el-date-picker v-model="form.publish_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="定价">
              <el-input-number v-model="form.price" :precision="2" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="语言">
              <el-input v-model="form.language" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="封面URL">
          <el-input v-model="form.cover_url" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="px-4 py-2 text-[14px] text-text-secondary rounded-standard border border-[rgba(0,0,0,0.1)] bg-transparent cursor-pointer hover:bg-apple-gray transition-colors tracking-[-0.224px] mr-2" @click="dialogVisible = false">取消</button>
        <button class="px-4 py-2 bg-apple-blue text-white text-[14px] rounded-standard border-none cursor-pointer hover:opacity-90 transition-opacity tracking-[-0.224px]" @click="handleSubmit">确定</button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* Apple Form */
.apple-form :deep(.el-form-item__label) {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: #1d1d1f !important;
  letter-spacing: -0.224px !important;
}
</style>
