<template>
  <div class="batch">
    <h2 class="page-title">📋 批量录入</h2>
    <div class="card">
      <p class="batch-hint">逐条添加历史体重数据，支持一次性批量保存</p>
      <div class="batch-list">
        <div class="batch-row" v-for="(item, index) in items" :key="index">
          <input
            type="date"
            v-model="item.date"
            :max="today"
            class="input-field batch-date"
          />
          <input
            type="number"
            v-model="item.weight"
            step="0.1"
            min="1"
            max="500"
            placeholder="体重 kg"
            class="input-field batch-weight"
          />
          <button class="btn btn-sm batch-remove" @click="removeRow(index)">✕</button>
        </div>
      </div>
      <div class="batch-actions">
        <button class="btn btn-secondary" @click="addRow">+ 添加一行</button>
        <button class="btn btn-primary" :disabled="loading" @click="handleSubmit">
          {{ loading ? '保存中...' : `批量保存 (${items.length}条)` }}
        </button>
      </div>
      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
      <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const today = new Date().toISOString().split('T')[0]
const items = ref([{ date: today, weight: '' }])
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const addRow = () => {
  items.value.push({ date: today, weight: '' })
}

const removeRow = (index) => {
  if (items.value.length > 1) {
    items.value.splice(index, 1)
  }
}

const handleSubmit = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  const validItems = items.value.filter(i => i.date && i.weight && parseFloat(i.weight) > 0 && parseFloat(i.weight) <= 500)
  if (validItems.length === 0) {
    errorMsg.value = '请至少输入一条有效记录'
    return
  }

  loading.value = true
  try {
    const token = localStorage.getItem('user_token')
    const records = validItems.map(i => ({
      record_date: i.date,
      weight: parseFloat(i.weight)
    }))
    const res = await axios.post('/api/weights/batch', { records }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    successMsg.value = res.data.message
    items.value = [{ date: today, weight: '' }]
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.batch-hint {
  color: var(--text-light);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.batch-list { margin-bottom: var(--spacing-md); }

.batch-row {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.batch-date { flex: 1; max-width: 200px; }
.batch-weight { flex: 1; }
.batch-remove {
  background: var(--bg-primary);
  color: var(--color-danger);
  font-size: var(--font-size-base);
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}
.batch-remove:hover { background: var(--color-danger); color: white; }
.batch-actions {
  display: flex; gap: var(--spacing-md); align-items: center;
}
.error-msg {
  color: var(--color-danger); font-size: var(--font-size-xs); margin-top: var(--spacing-sm);
}
.success-msg {
  color: var(--color-success); font-size: var(--font-size-sm); margin-top: var(--spacing-sm);
}
@media screen and (max-width: 767px) {
  .batch-row { flex-wrap: wrap; }
  .batch-date { max-width: 100%; flex: 1 1 100%; }
  .batch-weight { flex: 2; }
  .batch-actions { flex-direction: column; width: 100%; }
  .batch-actions .btn { width: 100%; }
}
</style>
