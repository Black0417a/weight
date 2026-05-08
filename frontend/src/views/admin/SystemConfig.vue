<template>
  <div class="system-config">
    <h2 class="page-title">系统设置</h2>
    <div class="card">
      <table class="data-table" v-if="configs.length > 0">
        <thead>
          <tr>
            <th>配置项</th>
            <th>值</th>
            <th>说明</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in configs" :key="c.id">
            <td><code>{{ c.key }}</code></td>
            <td>{{ c.value }}</td>
            <td>{{ c.description }}</td>
            <td>
              <button class="btn btn-sm btn-secondary" @click="editConfig(c)">编辑</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <p class="empty-state-text">暂无配置项</p>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">编辑配置</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="form-group">
          <label>配置项</label>
          <p style="font-weight:600">{{ editForm.key }}</p>
        </div>
        <div class="form-group">
          <label>值</label>
          <input v-model="editForm.value" class="input-field" />
        </div>
        <div class="form-group">
          <label>说明</label>
          <input v-model="editForm.description" class="input-field" />
        </div>
        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <button class="btn btn-primary" style="width:100%" :disabled="saving" @click="handleSave">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const configs = ref([])
const showModal = ref(false)
const saving = ref(false)
const errorMsg = ref('')
const editForm = ref({ key: '', value: '', description: '' })

const fetchConfigs = async () => {
  try {
    const res = await request.get('/admin/configs')
    configs.value = res
  } catch (err) { console.error(err) }
}

const editConfig = (config) => {
  editForm.value = { ...config }
  showModal.value = true
}

const handleSave = async () => {
  errorMsg.value = ''
  saving.value = true
  try {
    await request.put(`/admin/configs/${editForm.value.key}`, {
      value: editForm.value.value,
      description: editForm.value.description
    })
    showModal.value = false
    await fetchConfigs()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally { saving.value = false }
}

onMounted(fetchConfigs)
</script>

<style scoped>
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

code {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
}

.form-group { margin-bottom: var(--spacing-md); }

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.error-msg { color: var(--color-danger); font-size: var(--font-size-xs); margin-bottom: var(--spacing-sm); }
</style>
