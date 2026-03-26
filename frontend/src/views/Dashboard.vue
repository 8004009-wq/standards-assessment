<template>
  <div>
    <h2>控制台</h2>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total_tasks || 0 }}</div>
            <div class="stat-label">总任务数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.completed_tasks || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.average_score || 0 }}</div>
            <div class="stat-label">平均得分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value" :class="getLevelColor(stats.level_distribution?.优秀)">{{ stats.level_distribution?.优秀 || 0 }}</div>
            <div class="stat-label">优秀</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>快速入口</template>
      <el-space>
        <el-button type="primary" @click="$router.push('/templates')">新建评估模版</el-button>
        <el-button type="success" @click="$router.push('/tasks')">新建评估任务</el-button>
        <el-button @click="$router.push('/stats')">查看统计</el-button>
      </el-space>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({})

const getLevelColor = (val) => {
  if (val > 0) return 'text-success'
  return ''
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/stats/overview')
    stats.value = res.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  color: #909399;
  margin-top: 5px;
}

.text-success {
  color: #67c23a;
}
</style>
