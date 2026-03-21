<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getCopies, createCopy, updateCopy, deleteCopy, getBooks } from '@/api/books'
import { COPY_STATUS, COPY_CONDITION, getStatusTagType } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const copies = ref([])
const books = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)

const queryParams = ref({ book: '', status: '', page: 1, page_size: 10 })

const form = reactive({
  id: null, book_id: null, barcode: '', condition: 1, status: 1, location: ''
})

const rules = {
  book_id: [{ required: true, message: '请选择图书', trigger: 'change' }],
  barcode: [{ required: true, message: '请输入条码', trigger: 'blur' }]
}

async function fetchCopies() {
  loading.value = true
  try {
    const params = { ...queryParams.value }
    if (!params.book) delete params.book
    if (params.status === '') delete params.status
    const data = await getCopies(params)
    copies.value = data.results || []
    total.value = data.count || 0
  } catch (error) {
    console.error('获取副本失败:', error)
  } finally {
    loading.value = false
  }
}

async function fetchBooks() {
  try {
    const data = await getBooks({ page_size: 1000 })
    books.value = data.results || []
  } catch (error) {
    console.error('获取图书失败:', error)
  }
}

function handleSearch() { queryParams.value.page = 1; fetchCopies() }
function handlePageChange(page) { queryParams.value.page = page; fetchCopies() }

function handleAdd() {
  dialogTitle.value = '入库'
  Object.assign(form, { id: null, book_id: null, barcode: '', condition: 1, status: 1, location: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑副本'
  Object.assign(form, { id: row.id, book_id: row.book_id, barcode: row.barcode, condition: row.condition, status: row.status, location: row.location || '' })
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    if (form.id) {
      await updateCopy(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createCopy(form)
      ElMessage.success('入库成功')
    }
    dialogVisible.value = false
    fetchCopies()
  } catch (error) {
    console.error('保存失败:', error)
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该副本吗？', '删除确认', { type: 'warning' })
    await deleteCopy(row.id)
    ElMessage.success('删除成功')
    fetchCopies()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => { fetchCopies(); fetchBooks() })
</script>

<template>
  <div class="page-container">
    <div class="search-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="queryParams.book" placeholder="选择图书" clearable filterable>
            <el-option v-for="book in books" :key="book.id" :label="book.title" :value="book.id" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="queryParams.status" placeholder="状态" clearable>
            <el-option v-for="(label, value) in COPY_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" icon="Search" @click="handleSearch">搜索</el-button>
          <el-button type="success" icon="Plus" @click="handleAdd">入库</el-button>
        </el-col>
      </el-row>
    </div>
    
    <div class="table-container">
      <el-table v-loading="loading" :data="copies" stripe>
        <el-table-column prop="book_title" label="图书" min-width="200" />
        <el-table-column prop="barcode" label="条码" width="150" />
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column prop="condition" label="品相" width="80">
          <template #default="{ row }">{{ COPY_CONDITION[row.condition] }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status, 'copy')">{{ COPY_STATUS[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="total > 0" class="pagination-container">
        <el-pagination v-model:current-page="queryParams.page" :page-size="queryParams.page_size" :total="total" layout="prev, pager, next, total" @current-change="handlePageChange" />
      </div>
    </div>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="图书" prop="book_id">
          <el-select v-model="form.book_id" placeholder="选择图书" filterable style="width: 100%">
            <el-option v-for="book in books" :key="book.id" :label="book.title" :value="book.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="条码" prop="barcode">
          <el-input v-model="form.barcode" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="form.location" placeholder="如：A区-03-2" />
        </el-form-item>
        <el-form-item label="品相">
          <el-select v-model="form.condition" style="width: 100%">
            <el-option v-for="(label, value) in COPY_CONDITION" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(label, value) in COPY_STATUS" :key="value" :label="label" :value="Number(value)" />
          </el-select>
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
