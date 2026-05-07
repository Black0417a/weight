<template>
  <div class="records">
    <h2 class="page-title">📝 体重记录</h2>
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>
    <div v-else-if="records.length === 0" class="card empty-state">
      <div class="empty-state-icon">📋</div>
      <p class="empty-state-text">还没有体重记录，快去记录吧</p>
    </div>
    <div v-else class="card">
      <table class="record-table">
        <thead>
          <tr>
            <th>日期</th>
            <th>体重 (kg)</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td class="td-date">{{ r.record_date }}</td>
            <td class="td-weight">{{ r.weight }}</td>
            <td class="td-action">
              <button class="btn btn-sm btn-delete" @click="handleDelete(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const records = ref([])
const loading = ref(true)

const fetchRecords = async () => {
  try {
    const token = localStorage.getItem('user_token')
    const res = await axios.get('/api/weights', {
      headers: { Authorization: `Bearer ${token}` }
    })
    records.value = res.data.reverse()
  } catch (err) {
    console.error('获取记录失败', err)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (record) => {
  if (!confirm(`确认删除 ${record.record_date} 的记录？`)) return
  try {
    const token = localStorage.getItem('user_token')
    await axios.delete(`/api/weights/${record.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchRecords()
  } catch (err) {
    alert('删除失败')
  }
}

onMounted(fetchRecords)
</script>

<style scoped>
.record-table {
  width: 100%;
  border-collapse: collapse;
}

.record-table th {
  text-align: left;
  padding: 12px 16px;
  color: var(--text-light);
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-bottom: 2px solid var(--bg-secondary);
}

.record-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--bg-secondary);
}

.td-date { color: var(--text-secondary); font-size: var(--font-size-sm); }
.td-weight { color: var(--color-primary); font-weight: 600; font-size: var(--font-size-lg); }
.td-action { text-align: right; }

.btn-delete {
  background: var(--bg-primary);
  color: var(--color-danger);
  border-radius: var(--radius-sm);
}

.btn-delete:hover { background: var(--color-danger); color: white; }
</style>
