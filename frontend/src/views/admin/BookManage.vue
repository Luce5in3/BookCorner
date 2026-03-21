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
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input v-model="queryParams.search" placeholder="搜索书名/作者" clearable @keyup.enter="handleSearch" />
        </el-col>
        <el-col :span="4">
          <el-tree-select v-model="queryParams.category" :data="categories" :props="{ label: 'name', value: 'id', children: 'children' }" placeholder="选择分类" clearable check-strictly />
        </el-col>
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option label="上架" :value="1" />
            <el-option label="下架" :value="0" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
          <el-button type="success" icon="Plus" @click="handleAdd">新增</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="books" stripe>
        <el-table-column prop="title" label="书名" min-width="200" />
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
            <el-tag :type="getStatusTagType(row.status, 'book')">{{ BOOK_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 0" type="success" link @click="handlePublish(row)">上架</el-button>
            <el-button v-else type="warning" link @click="handleUnpublish(row)">下架</el-button>
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
        <el-row :gutter="20">
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
        <el-row :gutter="20">
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
        <el-row :gutter="20">
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
        <el-row :gutter="20">
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-bar { background: #fff; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
.table-container { background: #fff; padding: 20px; border-radius: 4px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
