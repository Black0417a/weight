<template>
  <div class="admin-login-page">
    <div class="admin-login-card">
      <h1>⚙️ 管理后台</h1>
      <p class="subtitle">体重记录管理系统</p>

      <template v-if="mode === 'login'">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" class="input-field" placeholder="请输入用户名" @keyup.enter="handleLogin" />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" class="input-field" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
        <button class="btn btn-primary login-btn" :disabled="loading" @click="handleLogin">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <p class="switch-hint">
          还没有管理员？<a href="#" @click.prevent="switchToRegister">首次设置</a>
        </p>
      </template>

      <template v-else>
        <div class="setup-banner">
          <span>🔐</span>
          <p>创建首个管理员账户</p>
          <p class="setup-note">此功能仅在系统无管理员时可用</p>
        </div>
        <div class="form-group">
          <label>设置用户名</label>
          <input v-model="username" class="input-field" placeholder="至少3个字符" />
        </div>
        <div class="form-group">
          <label>设置密码</label>
          <input v-model="password" type="password" class="input-field" placeholder="至少6个字符" />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
        <button class="btn btn-primary login-btn" :disabled="loading" @click="handleRegister">
          {{ loading ? '创建中...' : '创建并激活' }}
        </button>
        <p class="switch-hint">
          <a href="#" @click.prevent="switchToLogin">返回登录</a>
        </p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)
const mode = ref('login')

const switchToRegister = () => {
  mode.value = 'register'
  errorMsg.value = ''
  successMsg.value = ''
  username.value = ''
  password.value = ''
}

const switchToLogin = () => {
  mode.value = 'login'
  errorMsg.value = ''
  successMsg.value = ''
  username.value = ''
  password.value = ''
}

const handleLogin = async () => {
  errorMsg.value = ''
  successMsg.value = ''
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

const handleRegister = async () => {
  errorMsg.value = ''
  successMsg.value = ''
  if (!username.value || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  if (username.value.length < 3) {
    errorMsg.value = '用户名至少3个字符'
    return
  }
  if (password.value.length < 6) {
    errorMsg.value = '密码至少6个字符'
    return
  }
  loading.value = true
  try {
    await request.post('/admin/auth/register', {
      username: username.value,
      password: password.value
    })
    successMsg.value = '管理员创建成功，正在登录...'
    setTimeout(async () => {
      try {
        await authStore.adminLogin(username.value, password.value)
        router.push('/admin/dashboard')
      } catch (err) {
        errorMsg.value = '自动登录失败，请手动登录'
        mode.value = 'login'
      } finally { loading.value = false }
    }, 500)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '注册失败'
    loading.value = false
  }
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

.success-msg {
  color: var(--color-success);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-sm);
}

.login-btn { width: 100%; background: #2c3e50; box-shadow: none; }
.login-btn:hover { background: #34495e; }

.switch-hint {
  text-align: center;
  margin-top: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--text-light);
}

.setup-banner {
  text-align: center;
  padding: var(--spacing-md);
  background: #fef3e2;
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
}

.setup-banner span { font-size: 32px; }

.setup-banner p {
  color: #e67e22;
  font-weight: 600;
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}

.setup-note {
  font-weight: 400 !important;
  font-size: var(--font-size-xs) !important;
  color: #b8860b !important;
}
</style>
