<template>
  <div>
    <h2>评估任务</h2>
    <el-card style="margin-top: 20px">
      <div style="display: flex; gap: 10px; margin-bottom: 15px">
        <el-button type="primary" @click="showCreate = true">新建评估任务</el-button>
        <el-button type="success" @click="showExcelImport = true">Excel 导入创建任务</el-button>
      </div>
      
      <el-table :data="tasks" style="margin-top: 20px" v-loading="loading">
        <el-table-column prop="task_name" label="任务名称" />
        <el-table-column prop="organization" label="评估组织" />
        <el-table-column prop="system_name" label="评估系统" />
        <el-table-column prop="template_name" label="评估模版" />
        <el-table-column prop="total_score" label="得分">
          <template #default="{ row }">
            {{ row.total_score ? row.total_score.toFixed(1) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">{{ row.level || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'processing' ? 'warning' : 'info'">
              {{ row.status === 'completed' ? '已完成' : row.status === 'processing' ? '评估中' : '待评估' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/tasks/${row.id}`)">详情</el-button>
            <el-button size="small" type="success" @click="startAssess(row.id)" :disabled="row.status !== 'pending'">开始评估</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreate" title="新建评估任务" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.task_name" placeholder="如：2024 年 DSMM 三级评估" />
        </el-form-item>
        <el-form-item label="评估组织">
          <el-input v-model="taskForm.organization" placeholder="如：XX 科技有限公司" />
        </el-form-item>
        <el-form-item label="评估系统">
          <el-input v-model="taskForm.system_name" placeholder="如：CRM 系统" />
        </el-form-item>
        <el-form-item label="评估模版">
          <el-select v-model="taskForm.template_id" style="width: 100%">
            <el-option v-for="t in templates" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务现状">
          <el-input v-model="taskForm.business_status" type="textarea" :rows="5" 
            placeholder="描述系统现状、已有的安全措施、文档等，用于大模型智能评估" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建任务</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showExcelImport" title="Excel 导入创建评估任务" width="600px">
      <el-alert type="info" style="margin-bottom: 15px" show-icon>
        <template #title>
          <div>Excel 表格应包含以下列（部分可选）：</div>
        </template>
        <div style="font-size: 12px; margin-top: 5px">
          必填：条款内容（或内容/条款）<br>
          可选：条款编号、评估要求、评估现状（或业务现状/现状）、能力域、PA、序号
        </div>
      </el-alert>
      
      <el-form :model="excelForm" label-width="100px">
        <el-form-item label="任务名称">
          <el-input v-model="excelForm.task_name" placeholder="如：2024 年 DSMM 三级评估" />
        </el-form-item>
        <el-form-item label="评估组织">
          <el-input v-model="excelForm.organization" placeholder="如：XX 科技有限公司" />
        </el-form-item>
        <el-form-item label="评估系统">
          <el-input v-model="excelForm.system_name" placeholder="如：CRM 系统" />
        </el-form-item>
        <el-form-item label="评估模版">
          <el-select v-model="excelForm.template_id" style="width: 100%">
            <el-option v-for="t in templates" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Excel 文件">
          <input type="file" @change="handleFileChange" accept=".xlsx,.xls" style="width: 100%" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showExcelImport = false">取消</el-button>
        <el-button type="success" @click="handleExcelImport" :loading="importing" :disabled="!selectedFile">导入并创建任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const creating = ref(false)
const importing = ref(false)
const showCreate = ref(false)
const showExcelImport = ref(false)
const tasks = ref([])
const templates = ref([])
const selectedFile = ref(null)

const taskForm = reactive({
  task_name: '',
  organization: '',
  system_name: '',
  template_id: null,
  business_status: ''
})

const excelForm = reactive({
  task_name: '',
  organization: '',
  system_name: '',
  template_id: null
})

const getLevelType = (level) => {
  const map = { '优秀': 'success', '良好': 'primary', '合格': 'warning', '不合格': 'danger' }
  return map[level] || 'info'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/tasks')
    tasks.value = res.data
  } catch (e) {
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    const res = await axios.get('/api/templates')
    templates.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const handleCreate = async () => {
  if (!taskForm.task_name || !taskForm.template_id) {
    ElMessage.warning('请填写任务名称并选择评估模版')
    return
  }
  
  creating.value = true
  try {
    await axios.post('/api/tasks', taskForm)
    ElMessage.success('任务创建成功')
    showCreate.value = false
    loadTasks()
  } catch (e) {
    ElMessage.error('创建任务失败')
  } finally {
    creating.value = false
  }
}

const handleFileChange = (event) => {
  selectedFile.value = event.target.files[0]
}

const handleExcelImport = async () => {
  if (!excelForm.task_name || !excelForm.template_id || !selectedFile.value) {
    ElMessage.warning('请填写任务名称、选择评估模版并上传 Excel 文件')
    return
  }
  
  importing.value = true
  try {
    const formData = new FormData()
    formData.append('task_name', excelForm.task_name)
    formData.append('organization', excelForm.organization)
    formData.append('system_name', excelForm.system_name)
    formData.append('template_id', excelForm.template_id)
    formData.append('file', selectedFile.value)
    
    const res = await axios.post('/api/tasks/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success(res.data.message || '任务创建成功')
    showExcelImport.value = false
    selectedFile.value = null
    excelForm.task_name = ''
    excelForm.organization = ''
    excelForm.system_name = ''
    excelForm.template_id = null
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

const startAssess = async (id) => {
  try {
    ElMessage.info('开始智能评估，这可能需要几分钟...')
    await axios.post(`/api/tasks/${id}/assess`)
    ElMessage.success('评估完成')
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '评估失败')
  }
}

onMounted(() => {
  loadTasks()
  loadTemplates()
})
</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}
</style>
