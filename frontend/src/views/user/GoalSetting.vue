<template>
  <div class="goal-page">
    <h2 class="page-title">🎯 目标体重</h2>
    <div class="card goal-card">
      <div v-if="currentGoal" class="current-goal">
        <p class="goal-label">当前目标</p>
        <p class="goal-value">{{ currentGoal.target_weight }} <span>kg</span></p>
      </div>
      <div class="form-group">
        <label for="target">{{ currentGoal ? '修改目标体重' : '设置目标体重' }}</label>
        <input
          id="target"
          v-model="targetWeight"
          type="number"
          step="0.1"
          min="1"
          max="500"
          class="input-field"
          placeholder="请输入目标体重 (kg)"
        />
      </div>
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
      <button class="btn btn-primary" :disabled="loading" @click="handleSave">
        {{ loading ? '保存中...' : '保存目标' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const currentGoal = ref(null)
const targetWeight = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

const fetchGoal = async () => {
  try {
    const res = await request.get('/goal')
    if (res.target_weight) {
      currentGoal.value = res
    }
  } catch (err) { console.error(err) }
}

const handleSave = async () => {
  errorMsg.value = ''
  successMsg.value = ''
  if (!targetWeight.value) {
    errorMsg.value = '请输入目标体重'
    return
  }
  const w = parseFloat(targetWeight.value)
  if (w <= 0 || w > 500) {
    errorMsg.value = '目标体重数值不合法'
    return
  }
  loading.value = true
  try {
    const res = await request.put('/goal', { target_weight: w })
    successMsg.value = '目标体重已保存'
    targetWeight.value = ''
    await fetchGoal()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally { loading.value = false }
}

onMounted(fetchGoal)
</script>

<style scoped>
.current-goal {
  text-align: center;
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
}

.goal-label { color: var(--text-light); font-size: var(--font-size-sm); margin-bottom: var(--spacing-xs); }

.goal-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-secondary);
}

.goal-value span { font-size: var(--font-size-base); font-weight: 400; color: var(--text-light); }

.form-group { margin-bottom: var(--spacing-md); }

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.error-msg { color: var(--color-danger); font-size: var(--font-size-xs); margin-bottom: var(--spacing-sm); }
.success-msg { color: var(--color-success); font-size: var(--font-size-sm); margin-bottom: var(--spacing-sm); }
</style>
