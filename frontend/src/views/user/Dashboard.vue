<template>
  <div class="dashboard">
    <h2 class="page-title">🏠 今日记录</h2>
    <div class="dash-grid">
      <div class="card quick-record">
        <h3 class="card-title">📝 快速记录</h3>
        <div class="form-group">
          <label>日期</label>
          <input
            type="date"
            v-model="recordDate"
            :max="today"
            class="input-field"
          />
        </div>
        <div class="form-group">
          <label>体重 (kg)</label>
          <input
            type="number"
            v-model="weight"
            step="0.1"
            min="1"
            max="500"
            class="input-field"
            placeholder="请输入体重"
            @keyup.enter="handleSubmit"
          />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <button class="btn btn-primary quick-btn" :disabled="loading" @click="handleSubmit">
          {{ loading ? '保存中...' : '记录体重' }}
        </button>
      </div>
      <div class="card last-record" v-if="lastRecord">
        <h3 class="card-title">📌 最近记录</h3>
        <p class="last-date">{{ lastRecord.record_date }}</p>
        <p class="last-weight">{{ lastRecord.weight }} <span>kg</span></p>
      </div>
      <div class="card goal-card">
        <h3 class="card-title">🎯 目标体重</h3>
        <p v-if="goal" class="goal-weight">{{ goal.target_weight }} <span>kg</span></p>
        <p v-else class="no-goal">尚未设置目标体重</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const today = new Date().toISOString().split('T')[0]
const recordDate = ref(today)
const weight = ref('')
const errorMsg = ref('')
const loading = ref(false)
const lastRecord = ref(null)
const goal = ref(null)

const fetchData = async () => {
  try {
    const token = localStorage.getItem('user_token')
    const headers = { Authorization: `Bearer ${token}` }

    const weightRes = await axios.get('/api/weights', {
      params: { end_date: today },
      headers
    })
    if (weightRes.data.length > 0) {
      lastRecord.value = weightRes.data[weightRes.data.length - 1]
    }

    const goalRes = await axios.get('/api/goal', { headers })
    if (goalRes.data.target_weight) {
      goal.value = goalRes.data
    }
  } catch (err) {
    console.error('获取数据失败', err)
  }
}

const handleSubmit = async () => {
  errorMsg.value = ''
  if (!weight.value) {
    errorMsg.value = '请输入体重'
    return
  }
  const w = parseFloat(weight.value)
  if (w <= 0 || w > 500) {
    errorMsg.value = '体重数值不合法'
    return
  }
  loading.value = true
  try {
    const token = localStorage.getItem('user_token')
    await axios.post('/api/weights', {
      weight: w,
      record_date: recordDate.value
    }, { headers: { Authorization: `Bearer ${token}` } })
    weight.value = ''
    await fetchData()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.dash-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-base);
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
  font-weight: 600;
}

.form-group {
  margin-bottom: var(--spacing-md);
}

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

.quick-btn {
  width: 100%;
  margin-top: var(--spacing-sm);
}

.last-date {
  font-size: var(--font-size-sm);
  color: var(--text-light);
  margin-bottom: var(--spacing-xs);
}

.last-weight {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-primary);
}

.last-weight span {
  font-size: var(--font-size-base);
  font-weight: 400;
  color: var(--text-light);
}

.goal-weight {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-secondary);
}

.goal-weight span {
  font-size: var(--font-size-base);
  font-weight: 400;
  color: var(--text-light);
}

.no-goal {
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

@media screen and (max-width: 767px) {
  .dash-grid { grid-template-columns: 1fr; gap: var(--spacing-md); }
  .last-weight, .goal-weight { font-size: var(--font-size-2xl); }
}
</style>
