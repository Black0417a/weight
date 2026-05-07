<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <h1>⚙️ 管理后台</h1>
      <p class="subtitle">体重记录管理系统</p>
      <div class="form-group">
        <label>用户名</label>
        <input v-model="username" class="input-field" placeholder="请输入用户名" @keyup.enter="handleLogin" />
      </div>
      <div class="form-group">
        <label>密码</label>
        <input v-model="password" type="password" class="input-field" placeholder="请输入密码" @keyup.enter="handleLogin" />
      </div>
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <button class="btn btn-primary login-btn" :disabled="loading" @click="handleLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleLogin = async () => {
  errorMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    await authStore.adminLogin(username.value, password.value)
    router.push('/admin/dashboard')
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '登录失败'
  } finally { loading.value = false }
}
</script>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2c3e50, #34495e);
  padding: var(--spacing-lg);
}

.admin-login-card {
  background: white;
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.admin-login-card h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: var(--spacing-xs);
}

.subtitle {
  text-align: center;
  color: var(--text-light);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xl);
}

.form-group { margin-bottom: var(--spacing-md); }

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.error-msg {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-sm);
}

.login-btn { width: 100%; background: #2c3e50; box-shadow: none; }
.login-btn:hover { background: #34495e; }
</style>
