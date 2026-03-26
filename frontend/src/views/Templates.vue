<template>
  <div>
    <h2>评估模版</h2>
    <el-card style="margin-top: 20px">
      <el-button type="primary" @click="showUpload = true">上传新标准</el-button>
      
      <el-table :data="templates" style="margin-top: 20px" v-loading="loading">
        <el-table-column prop="name" label="模版名称" />
        <el-table-column prop="level" label="标准等级" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="clauses_count" label="条款数量" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewTemplate(row.id)">查看条款</el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showUpload" title="上传标准文件" width="500px">
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="模版名称">
          <el-input v-model="uploadForm.name" placeholder="如：DSMM 三级评估标准" />
        </el-form-item>
        <el-form-item label="标准等级">
          <el-input v-model="uploadForm.level" placeholder="如：DSMM 三级" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="标准文件">
          <el-upload drag :auto-upload="false" :on-change="handleFileChange" accept=".pdf,.docx,.xlsx,.xls">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word 或 Excel 文件（Excel 为人工拆解的条款）</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">上传并拆解</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetail" title="条款详情" width="900px">
      <el-table :data="currentClauses">
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="sub_domain" label="PA" width="80" />
        <el-table-column prop="clause_number" label="标准编号" width="120" />
        <el-table-column prop="clause_content" label="条款内容" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const loading = ref(false)
const uploading = ref(false)
const showUpload = ref(false)
const showDetail = ref(false)
const templates = ref([])
const currentClauses = ref([])
const selectedFile = ref(null)

const uploadForm = reactive({
  name: '',
  level: '',
  description: ''
})

const loadTemplates = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/templates')
    templates.value = res.data
  } catch (e) {
    ElMessage.error('加载模版失败')
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleUpload = async () => {
  if (!uploadForm.name || !selectedFile.value) {
    ElMessage.warning('请填写模版名称并选择文件')
    return
  }
  
  uploading.value = true
  const formData = new FormData()
  formData.append('name', uploadForm.name)
  formData.append('level', uploadForm.level)
  formData.append('description', uploadForm.description || '')
  formData.append('file', selectedFile.value)
  
  try {
    const res = await axios.post('/api/templates/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(`上传成功！智能拆解出 ${res.data.clauses_count} 条条款`)
    showUpload.value = false
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const viewTemplate = async (id) => {
  try {
    const res = await axios.get(`/api/templates/${id}`)
    currentClauses.value = res.data.clauses
    showDetail.value = true
  } catch (e) {
    ElMessage.error('加载条款失败')
  }
}

const deleteTemplate = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该模版吗？删除后不可恢复。', '确认删除', { type: 'warning' })
  } catch {
    return
  }
  
  try {
    await axios.delete(`/api/templates/${id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}
</style>
