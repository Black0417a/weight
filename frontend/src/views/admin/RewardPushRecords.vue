<template>
  <div class="reward-push-records">
    <h2 class="page-title">奖励推送记录</h2>

    <div class="stats-bar">
      <div class="stats-item">
        <span class="stats-value">{{ pushStats.total_pushed }}</span>
        <span class="stats-label">总推送</span>
      </div>
      <div class="stats-item stats-unread">
        <span class="stats-value">{{ pushStats.unread_count }}</span>
        <span class="stats-label">未读</span>
      </div>
      <div class="stats-item stats-read">
        <span class="stats-value">{{ pushStats.read_count }}</span>
        <span class="stats-label">已读</span>
      </div>
    </div>

    <div class="card">
      <div class="toolbar">
        <input
          v-model="search"
          class="input-field search-input"
          placeholder="搜索用户邮箱..."
          @keyup.enter="handleSearch"
        />
        <select v-model="filterRuleId" class="input-field filter-select" @change="handleSearch">
          <option :value="null">全部规则</option>
          <option v-for="r in filterRules" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
        <select v-model="filterRead" class="input-field filter-select" @change="handleSearch">
          <option value="">全部状态</option>
          <option value="unread">未读</option>
          <option value="read">已读</option>
        </select>
        <select v-model="filterType" class="input-field filter-select" @change="handleSearch">
          <option value="">全部类型</option>
          <option value="weight_change">体重变化</option>
          <option value="goal_achievement">目标达成</option>
        </select>
        <button class="btn btn-primary" @click="handleSearch">搜索</button>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th>用户</th>
            <th>规则</th>
            <th>条件类型</th>
            <th>奖励类型</th>
            <th>当前体重</th>
            <th>变化/目标</th>
            <th>状态</th>
            <th>推送时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in records" :key="item.id">
            <td data-label="用户">{{ item.user_email }}</td>
            <td data-label="规则">{{ item.rule_name || '-' }}</td>
            <td data-label="条件类型">
              <span class="type-tag" :class="item.condition_type === 'weight_change' ? 'type-change' : 'type-goal'">
                {{ item.condition_type === 'weight_change' ? '体重变化' : '目标达成' }}
              </span>
            </td>
            <td data-label="奖励类型">
              <span class="type-tag" :class="item.reward_type === 'image' ? 'type-reward-image' : 'type-reward-text'">
                {{ item.reward_type === 'image' ? '图片' : '文字' }}
              </span>
            </td>
            <td data-label="当前体重">{{ item.weight_value ? item.weight_value + 'kg' : '-' }}</td>
            <td data-label="变化/目标">{{ item.target_weight ? item.target_weight + 'kg' : '-' }}</td>
            <td data-label="状态">
              <span :class="item.is_read ? 'tag-read' : 'tag-unread'">
                {{ item.is_read ? '已读' : '未读' }}
              </span>
            </td>
            <td data-label="推送时间">{{ formatTime(item.created_at) }}</td>
          </tr>
          <tr v-if="records.length === 0">
            <td colspan="8" class="empty-cell">暂无奖励推送记录</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="totalPages > 1">
        <button class="btn btn-sm btn-secondary" :disabled="page <= 1" @click="page--; fetchRecords()">上一页</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-sm btn-secondary" :disabled="page >= totalPages" @click="page++; fetchRecords()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const records = ref([])
const pushStats = ref({ total_pushed: 0, unread_count: 0, read_count: 0 })
const filterRules = ref([])
const search = ref('')
const filterRuleId = ref(null)
const filterRead = ref('')
const filterType = ref('')
const page = ref(1)
const totalPages = ref(1)

const fetchStats = async () => {
  try {
    const res = await request.get('/admin/reward-push-records/stats')
    pushStats.value = res
  } catch (err) { console.error(err) }
}

const fetchRecords = async () => {
  try {
    const params = {
      page: page.value,
      search: search.value
    }
    if (filterRuleId.value) params.rule_id = filterRuleId.value
    if (filterRead.value) params.is_read = filterRead.value
    if (filterType.value) params.condition_type = filterType.value

    const res = await request.get('/admin/reward-push-records', { params })
    records.value = res.records
    totalPages.value = res.pages
    filterRules.value = res.rules
  } catch (err) { console.error(err) }
}

const handleSearch = () => {
  page.value = 1
  fetchRecords()
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const match = timeStr.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})/)
  if (match) {
    return `${match[1]} ${match[2]}`
  }
  const d = new Date(timeStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  fetchStats()
  fetchRecords()
})
</script>

<style scoped>
.stats-bar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.stats-item {
  flex: 1;
  background: white;
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.stats-value {
  display: block;
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: #2c3e50;
}

.stats-label {
  font-size: var(--font-size-xs);
  color: var(--text-light);
  margin-top: 4px;
}

.stats-unread .stats-value { color: var(--color-secondary); }
.stats-read .stats-value { color: var(--color-success); }

.toolbar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.search-input { flex: 1; min-width: 180px; max-width: 280px; }
.filter-select { width: 140px; }

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 10px 12px;
  font-size: var(--font-size-xs);
  color: var(--text-light);
  border-bottom: 2px solid #eee;
  white-space: nowrap;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: var(--font-size-sm);
}

.type-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.type-change { background: #e3f2fd; color: #1565c0; }
.type-goal { background: #e8f5e9; color: #2e7d32; }
.type-reward-text { background: #fff3e0; color: #e65100; }
.type-reward-image { background: #f3e5f5; color: #7b1fa2; }

.tag-unread {
  background: #ffe8e8;
  color: var(--color-primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.tag-read {
  background: #e8e8e8;
  color: #888;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.empty-cell { text-align: center; color: var(--text-light); padding: 24px; }

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.page-info { font-size: var(--font-size-sm); color: var(--text-secondary); }

@media screen and (max-width: 767px) {
  .stats-bar {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .toolbar {
    flex-direction: column;
  }

  .search-input { max-width: 100%; }
  .filter-select { width: 100%; }

  .data-table {
    display: block;
    width: 100%;
  }

  .data-table thead { display: none; }

  .data-table tbody { display: block; }

  .data-table tr {
    display: block;
    margin-bottom: var(--spacing-md);
    border: 1px solid #eee;
    border-radius: var(--radius-md);
    padding: var(--spacing-sm);
  }

  .data-table td {
    display: block;
    border: none;
    position: relative;
    padding: 8px 8px 8px 50%;
    white-space: normal;
    text-align: right;
    font-size: var(--font-size-xs);
  }

  .data-table td::before {
    content: attr(data-label);
    position: absolute;
    left: 8px;
    width: 45%;
    font-weight: 500;
    text-align: left;
    color: var(--text-secondary);
    font-size: var(--font-size-xs);
  }

  .pagination {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }
}
</style>
