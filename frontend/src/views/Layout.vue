<template>
  <el-container>
    <el-aside width="220px">
      <div class="logo">标准智能评估</div>
      <el-menu :default-active="activeMenu" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>控制台</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Document /></el-icon>
          <span>评估模版</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>评估任务</span>
        </el-menu-item>
        <el-menu-item index="/stats">
          <el-icon><TrendCharts /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
        <el-divider style="border-color: #4a5568; margin: 8px 0" />
        <el-menu-item index="/admin">
          <el-icon><Setting /></el-icon>
          <span>管理员</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <span>欢迎，{{ username }}</span>
          <el-button size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, Document, List, TrendCharts, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const username = ref(localStorage.getItem('username') || '用户')

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.el-container {
  min-height: 100vh;
}

.el-aside {
  background: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  background: #2b3a4b;
}

.el-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.el-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
