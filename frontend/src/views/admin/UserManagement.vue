<template>
  <div class="user-management">
    <h2 class="page-title">用户管理</h2>
    <div class="card">
      <div class="toolbar">
        <input v-model="search" class="input-field search-input" placeholder="搜索邮箱..." @keyup.enter="fetchUsers" />
        <button class="btn btn-primary" @click="fetchUsers">搜索</button>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>邮箱</th>
            <th>记录数</th>
            <th>注册时间</th>
            <th>邮件提醒</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td data-label="ID">{{ u.id }}</td>
            <td data-label="邮箱">{{ u.email }}</td>
            <td data-label="记录数">{{ u.record_count }}</td>
            <td data-label="注册时间">{{ u.created_at ? new Date(u.created_at).toLocaleDateString('zh-CN') : '-' }}</td>
            <td data-label="邮件提醒">
              <label class="toggle-switch">
                <input type="checkbox" :checked="u.email_reminder_enabled" @change="toggleEmailReminder(u)" />
                <span class="slider"></span>
              </label>
            </td>
            <td data-label="操作" class="actions">
              <button class="btn btn-sm btn-secondary" @click="showDetail(u)">详情</button>
              <button class="btn btn-sm btn-delete" @click="handleDelete(u)">删除</button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="empty-cell">暂无数据</td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn btn-sm btn-secondary" :disabled="page <= 1" @click="page--; fetchUsers()">上一页</button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-sm btn-secondary" :disabled="page >= totalPages" @click="page++; fetchUsers()">下一页</button>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">用户详情</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div v-if="detailUser">
          <p><strong>邮箱：</strong>{{ detailUser.email }}</p>
          <p><strong>记录数：</strong>{{ detailUser.record_count }}</p>
          <h4 style="margin-top:16px">体重记录</h4>
          <table class="data-table" v-if="detailRecords.length > 0">
            <thead><tr><th>日期</th><th>体重</th></tr></thead>
            <tbody>
              <tr v-for="r in detailRecords" :key="r.id">
                <td>{{ r.record_date }}</td>
                <td>{{ r.weight }} kg</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="empty-cell">暂无记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const users = ref([])
const search = ref('')
const page = ref(1)
const totalPages = ref(1)
const showModal = ref(false)
const detailUser = ref(null)
const detailRecords = ref([])

const fetchUsers = async () => {
  try {
    const res = await request.get('/admin/users', {
      params: { page: page.value, search: search.value }
    })
    users.value = res.users
    totalPages.value = res.pages
  } catch (err) { console.error(err) }
}

const showDetail = async (user) => {
  try {
    const res = await request.get(`/admin/users/${user.id}`)
    detailUser.value = res.user
    detailRecords.value = res.weight_records
    showModal.value = true
  } catch (err) { console.error(err) }
}

const handleDelete = async (user) => {
  if (!confirm(`确认删除用户 ${user.email}？`)) return
  try {
    await request.delete(`/admin/users/${user.id}`)
    await fetchUsers()
  } catch (err) { alert('删除失败') }
}

const toggleEmailReminder = async (user) => {
  const originalState = user.email_reminder_enabled
  try {
    // 先临时更新UI
    user.email_reminder_enabled = !originalState
    const res = await request.put(`/admin/users/${user.id}/email-reminder`, {
      enabled: user.email_reminder_enabled
    })
    // 用API返回的状态确认
    user.email_reminder_enabled = res.email_reminder_enabled
  } catch (err) {
    // 出错时恢复原状
    user.email_reminder_enabled = originalState
    alert('设置失败')
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #4CAF50;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.toolbar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.search-input { flex: 1; max-width: 300px; }

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
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: var(--font-size-sm);
}

.actions { display: flex; gap: var(--spacing-xs); }

.btn-delete { background: #fff5f5; color: var(--color-danger); }
.btn-delete:hover { background: var(--color-danger); color: white; }

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
  .data-table {
    display: block;
    width: 100%;
  }

  .data-table thead {
    display: none;
  }

  .data-table tbody {
    display: block;
  }

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

  .data-table td.actions {
    padding-left: 0;
    text-align: center;
    display: flex;
    gap: 8px;
    justify-content: center;
    border-bottom: none;
  }

  .data-table td.actions::before {
    display: none;
  }

  .data-table td:nth-child(5) {
    padding-top: 8px;
    padding-bottom: 8px;
  }

  .data-table td:nth-child(5)::before {
    top: 8px;
  }

  .toolbar {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .pagination {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .modal-content {
    max-height: 85vh;
    overflow-y: auto;
  }
}
</style>
