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
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.record_count }}</td>
            <td>{{ u.created_at ? new Date(u.created_at).toLocaleDateString('zh-CN') : '-' }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" @click="showDetail(u)">详情</button>
              <button class="btn btn-sm btn-delete" @click="handleDelete(u)">删除</button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="5" class="empty-cell">暂无数据</td>
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

onMounted(fetchUsers)
</script>

<style scoped>
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
</style>
