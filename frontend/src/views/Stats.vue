<template>
  <div>
    <h2>统计分析</h2>
    
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
            <div class="stat-value">{{ stats.level_distribution?.优秀 || 0 }}</div>
            <div class="stat-label">优秀</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>等级分布</template>
          <div class="chart-container">
            <div class="level-bar" v-for="(count, level) in stats.level_distribution" :key="level">
              <span class="level-name">{{ level }}</span>
              <el-progress :percentage="getPercentage(count)" :status="getLevelStatus(level)" />
              <span class="level-count">{{ count }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>评估等级说明</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="优秀 (85-100 分)">
              <el-tag type="success">完全符合标准要求</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="良好 (75-85 分)">
              <el-tag type="primary">基本符合，有少量不足</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="合格 (60-74 分)">
              <el-tag type="warning">达到基本要求</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="不合格 (0-59 分)">
              <el-tag type="danger">需要大幅改进</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({})

const getPercentage = (count) => {
  const total = stats.value.completed_tasks || 1
  return Math.round((count / total) * 100)
}

const getLevelStatus = (level) => {
  const map = { '优秀': 'success', '良好': 'success', '合格': 'warning', '不合格': 'exception' }
  return map[level] || ''
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

.chart-container {
  padding: 20px;
}

.level-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.level-name {
  width: 60px;
  font-weight: bold;
}

.level-count {
  width: 40px;
  text-align: right;
}
</style>
