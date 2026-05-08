<template>
  <div class="records-page">
    <div class="records-header">
      <h2 class="page-title">体重记录</h2>
      <button class="btn-add" @click="openAddModal">+</button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>

    <div v-else-if="records.length === 0" class="card empty-state">
      <div class="empty-state-icon">📋</div>
      <p class="empty-state-text">还没有体重记录</p>
      <p class="empty-state-hint">点击右上角 + 开始记录</p>
    </div>

    <div v-else class="card">
      <div class="record-list">
        <div class="record-row" v-for="r in records" :key="r.id">
          <div class="record-left">
            <span class="record-date">{{ formatDate(r.record_date) }}</span>
            <span class="record-weekday">{{ getWeekday(r.record_date) }}</span>
          </div>
          <span class="record-weight">{{ r.weight }} <small>kg</small></span>
          <button class="btn-delete" @click="handleDelete(r)">✕</button>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">记录体重</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="form-group">
          <label>日期</label>
          <input type="date" v-model="addDate" :max="today" class="input-field" />
        </div>
        <div class="form-group">
          <label>体重 (kg)</label>
          <input
            type="number"
            v-model="addWeight"
            step="0.1"
            min="1"
            max="500"
            class="input-field input-weight"
            placeholder="0.0"
            autofocus
            @keyup.enter="handleAdd"
          />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <button class="btn btn-primary add-btn" :disabled="saving" @click="handleAdd">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const today = new Date().toISOString().split('T')[0]
const records = ref([])
const loading = ref(true)
const showModal = ref(false)
const addDate = ref(today)
const addWeight = ref('')
const errorMsg = ref('')
const saving = ref(false)

const formatDate = (d) => {
  const parts = d.split('-')
  return `${parts[1]}/${parts[2]}`
}

const getWeekday = (d) => {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const date = new Date(d)
  return days[date.getDay()]
}

const fetchRecords = async () => {
  try {
    const res = await request.get('/weights')
    records.value = res.reverse()
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  addDate.value = today
  addWeight.value = ''
  errorMsg.value = ''
  showModal.value = true
}

const handleAdd = async () => {
  errorMsg.value = ''
  if (!addWeight.value) {
    errorMsg.value = '请输入体重'
    return
  }
  const w = parseFloat(addWeight.value)
  if (w <= 0 || w > 500) {
    errorMsg.value = '体重数值不合法'
    return
  }
  saving.value = true
  try {
    await request.post('/weights', {
      weight: w,
      record_date: addDate.value
    })
    showModal.value = false
    await fetchRecords()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally {
    saving.value = false
  }
}

const handleDelete = async (record) => {
  if (!confirm(`删除 ${record.record_date} 的记录？`)) return
  try {
    await request.delete(`/weights/${record.id}`)
    await fetchRecords()
  } catch (err) {
    alert('删除失败')
  }
}

onMounted(fetchRecords)
</script>

<style scoped>
.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.records-header .page-title { margin-bottom: 0; }

.btn-add {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255,107,107,0.3);
  transition: transform 0.2s ease;
}

.btn-add:hover { transform: scale(1.1); }

.record-list { }

.record-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #fef0f0;
}

.record-row:last-child { border-bottom: none; }

.record-left {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.record-date {
  font-size: var(--font-size-base);
  color: var(--text-primary);
  font-weight: 500;
}

.record-weekday {
  font-size: var(--font-size-xs);
  color: var(--text-light);
}

.record-weight {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-primary);
  margin-right: var(--spacing-md);
}

.record-weight small {
  font-size: var(--font-size-xs);
  font-weight: 400;
  color: var(--text-light);
}

.btn-delete {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-primary);
  color: var(--text-light);
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-delete:hover { background: var(--color-danger); color: white; }

.form-group { margin-bottom: var(--spacing-md); }

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.input-weight {
  font-size: 28px;
  font-weight: 600;
  text-align: center;
  height: 60px;
}

.error-msg {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-sm);
}

.add-btn { width: 100%; }

.empty-state-hint {
  font-size: var(--font-size-xs);
  color: var(--text-light);
  margin-top: var(--spacing-xs);
}
</style>
