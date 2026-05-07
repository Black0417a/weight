<template>
  <div class="admin-dashboard">
    <h2 class="page-title">仪表盘</h2>
    <div class="stats-grid">
      <div class="card stat-card">
        <p class="stat-icon">👥</p>
        <p class="stat-value">{{ stats.user_count }}</p>
        <p class="stat-label">用户总数</p>
      </div>
      <div class="card stat-card">
        <p class="stat-icon">📝</p>
        <p class="stat-value">{{ stats.record_count }}</p>
        <p class="stat-label">记录总数</p>
      </div>
      <div class="card stat-card">
        <p class="stat-icon">🎁</p>
        <p class="stat-value">{{ stats.active_rule_count }}</p>
        <p class="stat-label">活跃规则</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({ user_count: 0, record_count: 0, active_rule_count: 0 })

const fetchStats = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.get('/api/admin/dashboard/stats', {
      headers: { Authorization: `Bearer ${token}` }
    })
    stats.value = res.data
  } catch (err) { console.error(err) }
}

onMounted(fetchStats)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-xl);
}

.stat-icon { font-size: 36px; margin-bottom: var(--spacing-sm); }
.stat-value { font-size: var(--font-size-3xl); font-weight: 700; color: #2c3e50; }
.stat-label { font-size: var(--font-size-sm); color: var(--text-light); margin-top: var(--spacing-xs); }

@media screen and (max-width: 767px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>
