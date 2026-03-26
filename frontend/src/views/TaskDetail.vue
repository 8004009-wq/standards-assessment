<template>
  <div>
    <el-page-header @back="$router.back()" :title="task.task_name">
      <template #extra>
        <el-button type="warning" @click="saveStatus" :disabled="task.status === 'completed'">保存业务现状</el-button>
        <el-button type="primary" @click="startAssess" :disabled="task.status === 'completed' || !hasClauses">开始智能评估</el-button>
        <el-button type="success" @click="downloadReport" :disabled="!task.total_score">下载报告</el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card>
          <div class="info-item">
            <label>评估组织</label>
            <div>{{ task.organization || '-' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="info-item">
            <label>评估系统</label>
            <div>{{ task.system_name || '-' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="score-card">
            <div class="score-value" :class="getScoreColor(task.total_score)">
              {{ task.total_score ? task.total_score.toFixed(1) : '-' }}
            </div>
            <div class="score-label">评估得分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="score-card">
            <div class="score-value" :class="getLevelColor(task.level)">
              {{ task.level || '-' }}
            </div>
            <div class="score-label">评估等级</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-alert type="info" style="margin-top: 20px" show-icon>
      <template #title>
        <div>请在下方表格中填写每条条款的业务现状，然后点击"保存业务现状"，最后点击"开始智能评估"</div>
      </template>
    </el-alert>

    <el-card style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>条款列表 (共 {{ task.results.length }} 条)</span>
          <el-tag :type="task.status === 'completed' ? 'success' : 'warning'">
            {{ task.status === 'completed' ? '已完成评估' : '待评估' }}
          </el-tag>
        </div>
      </template>
      <el-table :data="task.results" v-loading="loading" max-height="600">
        <el-table-column prop="seq" label="序号" width="60" fixed />
        <el-table-column prop="sub_domain" label="PA" width="80" />
        <el-table-column prop="clause_number" label="标准编号" width="100" />
        <el-table-column prop="clause_content" label="条款内容" min-width="250" />
        <el-table-column label="业务现状" min-width="300">
          <template #default="{ row }">
            <el-input
              v-if="task.status !== 'completed'"
              v-model="row.business_status"
              type="textarea"
              :rows="2"
              placeholder="填写该条款对应的业务现状、已有措施、文档等"
            />
            <div v-else style="white-space: pre-wrap; font-size: 12px">{{ row.business_status || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="评估结果" width="100" v-if="task.status === 'completed'">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="得分" width="80" v-if="task.status === 'completed'" />
        <el-table-column prop="comment" label="评语" min-width="200" v-if="task.status === 'completed'" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const assessing = ref(false)
const task = reactive({
  id: route.params.id,
  task_name: '',
  organization: '',
  system_name: '',
  template_name: '',
  business_status: '',
  total_score: null,
  level: '',
  status: 'pending',
  results: []
})

const hasClauses = computed(() => task.results.length > 0)

const getScoreColor = (score) => {
  if (score >= 85) return 'text-success'
  if (score >= 75) return 'text-primary'
  if (score >= 60) return 'text-warning'
  return 'text-danger'
}

const getLevelColor = (level) => {
  const map = { '优秀': 'text-success', '良好': 'text-primary', '合格': 'text-warning', '不合格': 'text-danger' }
  return map[level] || ''
}

const getResultType = (result) => {
  const map = { '符合': 'success', '部分符合': 'warning', '不符合': 'danger', '不适用': 'info' }
  return map[result] || 'info'
}

const loadTask = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/tasks/${route.params.id}`)
    Object.assign(task, res.data)
  } catch (e) {
    ElMessage.error('加载任务详情失败')
  } finally {
    loading.value = false
  }
}

const saveStatus = async () => {
  if (!hasClauses.value) {
    ElMessage.warning('暂无条款数据')
    return
  }
  
  saving.value = true
  try {
    const items = task.results.map(r => ({
      clause_id: r.clause_id,
      business_status: r.business_status || ''
    }))
    
    await axios.post(`/api/tasks/${task.id}/save-all-status`, items)
    ElMessage.success('业务现状已保存')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const startAssess = async () => {
  if (!hasClauses.value) {
    ElMessage.warning('暂无条款数据')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '开始智能评估后，系统将对 263 条条款逐一评估，这可能需要几分钟。确认开始？',
      '确认开始评估',
      { type: 'warning' }
    )
  } catch {
    return
  }
  
  assessing.value = true
  try {
    ElMessage.info('开始智能评估，这可能需要几分钟...')
    await axios.post(`/api/tasks/${task.id}/assess`)
    ElMessage.success('评估完成')
    await loadTask()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '评估失败')
  } finally {
    assessing.value = false
  }
}

const downloadReport = async () => {
  try {
    const res = await axios.get(`/api/tasks/${route.params.id}/report`)
    ElMessage.success(`报告已生成：${res.data.report_path}`)
  } catch (e) {
    ElMessage.error('生成报告失败')
  }
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.info-item {
  margin-bottom: 15px;
}

.info-item label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 5px;
}

.score-card {
  text-align: center;
  padding: 20px;
}

.score-value {
  font-size: 42px;
  font-weight: bold;
}

.score-label {
  color: #909399;
  margin-top: 10px;
}

.text-success { color: #67c23a; }
.text-primary { color: #409EFF; }
.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }
</style>
