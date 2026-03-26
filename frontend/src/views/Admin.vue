<template>
  <div>
    <h2>管理员 - 账号管理</h2>
    
    <el-card style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>账号列表</span>
          <el-button type="primary" size="small" @click="showCreate = true">新建账号</el-button>
        </div>
      </template>
      
      <el-table :data="accounts" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="resetPassword(row)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreate" title="新建账号" width="400px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" placeholder="请输入密码（至少 8 位）" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPassword" title="账号密码" width="400px">
      <el-alert type="success" show-icon>
        <template #title>
          <div>
            <p>用户名：<strong>{{ currentAccount.username }}</strong></p>
            <p>密码：<strong style="font-size: 18px; color: #f56c6c">{{ currentAccount.password }}</strong></p>
            <p style="margin-top: 10px; font-size: 12px; color: #909399">请妥善保存密码，关闭后将不再显示</p>
          </div>
        </template>
      </el-alert>
      <template #footer>
        <el-button type="primary" @click="showPassword = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const creating = ref(false)
const showCreate = ref(false)
const showPassword = ref(false)
const accounts = ref([])
const currentAccount = reactive({ username: '', password: '' })

const newUser = reactive({ username: '', password: '' })

const loadAccounts = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/auth/accounts')
    accounts.value = res.data
  } catch (e) {
    ElMessage.error('加载账号列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!newUser.username || !newUser.password || newUser.password.length < 8) {
    ElMessage.warning('用户名和密码不能为空，密码至少 8 位')
    return
  }
  
  creating.value = true
  try {
    await axios.post('/api/auth/accounts', newUser)
    ElMessage.success('账号创建成功')
    showCreate.value = false
    loadAccounts()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

const resetPassword = async (account) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 "${account.username}" 的密码吗？`,
      '确认重置',
      { type: 'warning' }
    )
    
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    const newPassword = Array(16).fill(0).map(() => chars[Math.floor(Math.random() * chars.length)]).join('')
    
    await axios.post('/api/auth/accounts', {
      username: account.username + '_new',
      password: newPassword
    })
    
    currentAccount.username = account.username + '_new'
    currentAccount.password = newPassword
    showPassword.value = true
    loadAccounts()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('重置密码失败')
    }
  }
}

onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
h2 {
  margin-bottom: 20px;
}
</style>
