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

    <div class="card">
      <div class="profile-header-row">
        <h3 class="section-title">📋 个人资料</h3>
        <button
          v-if="!isEditing"
          class="btn btn-sm edit-btn"
          @click="startEdit"
        >
          编辑
        </button>
      </div>
      <div class="form-group">
        <label class="form-label">身高 (cm)</label>
        <input
          v-if="isEditing"
          type="number"
          v-model="editHeight"
          step="0.1"
          min="1"
          max="300"
          class="form-input"
          placeholder="请输入身高"
        />
        <p v-else class="form-value">{{ height || '未填写' }}</p>
      </div>
      <div class="form-group">
        <label class="form-label">生日</label>
        <input
          v-if="isEditing"
          type="date"
          v-model="editBirthday"
          class="form-input"
        />
        <p v-else class="form-value">{{ birthday || '未填写' }}</p>
      </div>
      <div v-if="computedAge !== null" class="age-display">
        年龄：<strong>{{ computedAge }}</strong> 岁
      </div>
      <div v-if="isEditing" class="edit-actions">
        <button class="btn btn-secondary cancel-btn" @click="cancelEdit">取消</button>
        <button class="btn btn-primary save-btn" :disabled="savingProfile" @click="handleSaveProfile">
          {{ savingProfile ? '保存中...' : '保存' }}
        </button>
      </div>
      <p v-if="profileMsg" class="profile-msg" :class="{ error: profileError }">{{ profileMsg }}</p>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()
const user = ref(null)
const reminderEnabled = ref(true)

const height = ref('')
const birthday = ref('')
const editHeight = ref('')
const editBirthday = ref('')
const isEditing = ref(false)
const savingProfile = ref(false)
const profileMsg = ref('')
const profileError = ref(false)

const displayBirthday = computed(() => {
  return isEditing.value ? editBirthday.value : birthday.value
})

const computedAge = computed(() => {
  if (!displayBirthday.value) return null
  const birth = new Date(displayBirthday.value)
  const today = new Date()
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--
  }
  return age >= 0 ? age : null
})

const fetchData = async () => {
  try {
    const res = await request.get('/auth/profile')
    user.value = res
    authStore.user = res
    localStorage.setItem('user_info', JSON.stringify(res))
    height.value = res.height || ''
    birthday.value = res.birthday || ''

    const remRes = await request.get('/reminder-settings')
    reminderEnabled.value = remRes.email_reminder_enabled
  } catch (err) { console.error(err) }
}

const startEdit = () => {
  editHeight.value = height.value
  editBirthday.value = birthday.value
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  editHeight.value = ''
  editBirthday.value = ''
  profileMsg.value = ''
}

const handleSaveProfile = async () => {
  profileMsg.value = ''
  profileError.value = false
  savingProfile.value = true

  try {
    const payload = {}
    if (editHeight.value !== '' && editHeight.value !== null) {
      payload.height = parseFloat(editHeight.value)
    }
    payload.birthday = editBirthday.value || null

    const res = await request.put('/auth/profile', payload)
    user.value = res.user
    authStore.user = res.user
    localStorage.setItem('user_info', JSON.stringify(res.user))
    height.value = res.user.height || ''
    birthday.value = res.user.birthday || ''

    isEditing.value = false
    profileMsg.value = '个人资料已保存'
  } catch (err) {
    profileError.value = true
    profileMsg.value = err.response?.data?.error || '保存失败'
  } finally {
    savingProfile.value = false
    setTimeout(() => { profileMsg.value = '' }, 3000)
  }
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

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0;
}

.profile-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.edit-btn {
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  background: var(--color-primary-light);
  color: var(--color-primary);
  border: none;
}

.edit-btn:hover {
  background: var(--color-primary);
  color: white;
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--text-light);
  margin-bottom: var(--spacing-xs);
}

.form-value {
  font-size: var(--font-size-base);
  color: var(--text-primary);
  font-weight: 500;
  padding: 10px 0;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e8e8e8;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--bg-primary);
  transition: border-color 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: var(--color-primary);
  outline: none;
  background: white;
}

.age-display {
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-md);
}

.age-display strong {
  color: var(--color-primary);
}

.save-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: var(--radius-full);
  font-size: var(--font-size-base);
}

.edit-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.cancel-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: var(--radius-full);
  font-size: var(--font-size-base);
  background: var(--bg-primary);
  color: var(--text-secondary);
  border: 2px solid #e8e8e8;
}

.cancel-btn:hover {
  border-color: var(--text-light);
  color: var(--text-primary);
}

.profile-msg {
  text-align: center;
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-sm);
  color: var(--color-success);
}

.profile-msg.error {
  color: var(--color-danger);
}

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
