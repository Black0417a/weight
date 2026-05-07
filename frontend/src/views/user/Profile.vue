<template>
  <div class="profile">
    <h2 class="page-title">👤 个人中心</h2>
    <div class="card">
      <div class="profile-info">
        <p class="info-label">邮箱地址</p>
        <p class="info-value">{{ user?.email || '未登录' }}</p>
      </div>
      <div class="profile-info">
        <p class="info-label">注册时间</p>
        <p class="info-value">{{ user?.created_at ? new Date(user.created_at).toLocaleDateString('zh-CN') : '-' }}</p>
      </div>
    </div>

    <div class="card reminder-card">
      <div class="reminder-row">
        <div>
          <p class="reminder-title">📧 邮箱提醒</p>
          <p class="reminder-desc">每晚20:00，若当天未记录体重，将发送邮件提醒</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="reminderEnabled" @change="toggleReminder" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>

    <div class="card">
      <button class="btn btn-secondary logout-btn" @click="handleLogout">退出登录</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()
const user = ref(null)
const reminderEnabled = ref(true)

const fetchData = async () => {
  try {
    const userInfo = localStorage.getItem('user_info')
    if (userInfo) { user.value = JSON.parse(userInfo) }

    const remRes = await request.get('/reminder-settings')
    reminderEnabled.value = remRes.email_reminder_enabled
  } catch (err) { console.error(err) }
}

const toggleReminder = async () => {
  try {
    await request.put('/reminder-settings', {
      email_reminder_enabled: reminderEnabled.value
    })
  } catch (err) { console.error(err) }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(fetchData)
</script>

<style scoped>
.profile-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--bg-secondary);
}

.profile-info:last-child { border-bottom: none; }

.info-label { color: var(--text-light); font-size: var(--font-size-sm); }
.info-value { color: var(--text-primary); font-weight: 500; font-size: var(--font-size-base); }

.reminder-card { margin-top: var(--spacing-md); }

.reminder-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reminder-title { font-weight: 600; font-size: var(--font-size-base); color: var(--text-primary); }

.reminder-desc {
  color: var(--text-light);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-xs);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 52px; height: 28px;
  flex-shrink: 0;
}

.toggle-switch input { opacity: 0; width: 0; height: 0; }

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background: #ddd;
  border-radius: 34px;
  transition: .3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 22px; width: 22px;
  left: 3px; bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: .3s;
}

input:checked + .toggle-slider { background: var(--color-primary); }
input:checked + .toggle-slider:before { transform: translateX(24px); }

.logout-btn {
  width: 100%;
  background: var(--bg-primary);
  color: var(--color-primary);
  border: 2px solid var(--color-primary-light);
  border-radius: var(--radius-full);
}

.logout-btn:hover { background: var(--color-danger); color: white; border-color: var(--color-danger); }
</style>
