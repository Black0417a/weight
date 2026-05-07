<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="login-icon">⚖️</span>
        <h1>体重记录小助手</h1>
        <p class="login-subtitle">坚持记录，遇见更好的自己</p>
      </div>
      <div class="login-body">
        <div class="input-group">
          <label for="email">邮箱地址</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="input-field"
            placeholder="请输入您的邮箱"
            @keyup.enter="handleLogin"
          />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <button class="btn btn-primary btn-lg login-btn" :disabled="loading" @click="handleLogin">
          <span v-if="loading" class="spinner-sm"></span>
          <span v-else>开始记录</span>
        </button>
        <p class="login-hint">首次输入邮箱将自动创建账户</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleLogin = async () => {
  errorMsg.value = ''
  if (!email.value.trim()) {
    errorMsg.value = '请输入邮箱地址'
    return
  }
  loading.value = true
  try {
    await authStore.login(email.value.trim())
    router.push('/dashboard')
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 50%, #ffd4d4 100%);
  padding: var(--spacing-lg);
}

.login-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-icon { font-size: 56px; display: block; margin-bottom: var(--spacing-md); }

.login-header h1 {
  font-size: var(--font-size-2xl);
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
}

.login-subtitle {
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.login-body { }
.input-group { margin-bottom: var(--spacing-md); }

.input-group label {
  display: block;
  margin-bottom: var(--spacing-sm);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.error-msg {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-sm);
}

.login-btn {
  width: 100%;
  margin-top: var(--spacing-sm);
}

.login-hint {
  text-align: center;
  margin-top: var(--spacing-md);
  color: var(--text-light);
  font-size: var(--font-size-xs);
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media screen and (max-width: 767px) {
  .login-card { padding: var(--spacing-xl); }
  .login-icon { font-size: 44px; }
  .login-header h1 { font-size: var(--font-size-xl); }
}
</style>
