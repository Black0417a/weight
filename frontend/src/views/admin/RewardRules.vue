<template>
  <div class="reward-rules">
    <h2 class="page-title">奖励规则</h2>
    <div class="card">
      <div style="margin-bottom:16px">
        <button class="btn btn-primary" @click="openCreate">+ 新建规则</button>
      </div>
      <div v-if="rules.length === 0" class="empty-state">
        <div class="empty-state-icon">🎁</div>
        <p class="empty-state-text">暂无奖励规则</p>
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>名称</th>
            <th>条件类型</th>
            <th>发放模式</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rules" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.condition_type === 'weight_change' ? '体重变化' : '目标达成' }}</td>
            <td>{{ r.grant_mode === 'auto' ? '自动' : '手动' }}</td>
            <td><span :class="r.is_active ? 'tag-active' : 'tag-inactive'">{{ r.is_active ? '启用' : '禁用' }}</span></td>
            <td class="actions">
              <button class="btn btn-sm btn-secondary" @click="openEdit(r)">编辑</button>
              <button class="btn btn-sm btn-delete" @click="handleDelete(r)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content" style="max-width:600px">
        <div class="modal-header">
          <h3 class="modal-title">{{ isEditing ? '编辑规则' : '新建规则' }}</h3>
          <button class="modal-close" @click="showModal = false">✕</button>
        </div>
        <div class="form-group">
          <label>规则名称</label>
          <input v-model="form.name" class="input-field" placeholder="请输入规则名称" />
        </div>
        <div class="form-group">
          <label>条件类型</label>
          <select v-model="form.condition_type" class="input-field">
            <option value="weight_change">体重变化幅度</option>
            <option value="goal_achievement">目标达成率</option>
          </select>
        </div>
        <div class="form-group" v-if="form.condition_type === 'weight_change'">
          <label>减重阈值 (天数)</label>
          <input v-model.number="form.condition_params.days" type="number" class="input-field" placeholder="如 7" />
          <label style="margin-top:8px">减重阈值 (kg)</label>
          <input v-model.number="form.condition_params.weight_kg" type="number" step="0.1" class="input-field" placeholder="如 2" />
        </div>
        <div class="form-group" v-if="form.condition_type === 'goal_achievement'">
          <label>达成率 (%)</label>
          <input v-model.number="form.condition_params.percentage" type="number" class="input-field" placeholder="如 80" />
        </div>
        <div class="form-group">
          <label>奖励类型</label>
          <select v-model="form.reward_type" class="input-field">
            <option value="text">文字</option>
            <option value="image">图片</option>
          </select>
        </div>
        <div class="form-group" v-if="form.reward_type === 'text'">
          <label>奖励内容</label>
          <textarea v-model="form.reward_content" class="input-field" rows="3" placeholder="请输入奖励文字内容"></textarea>
        </div>
        <div class="form-group" v-if="form.reward_type === 'image'">
          <label>上传图片</label>
          <input type="file" @change="onFileChange" accept="image/*" />
          <img v-if="form.reward_image" :src="form.reward_image" style="max-width:200px;margin-top:8px;border-radius:8px" />
        </div>
        <div class="form-group">
          <label>发放模式</label>
          <select v-model="form.grant_mode" class="input-field">
            <option value="auto">自动发放</option>
            <option value="manual">手动发放</option>
          </select>
        </div>
        <div class="form-group">
          <label>目标用户</label>
          <input v-model="form.target_users" class="input-field" placeholder="all 表示全部，或用逗号分隔用户ID" />
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="form.is_active" /> 启用规则
          </label>
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
import axios from 'axios'

const rules = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const errorMsg = ref('')
const selectedFile = ref(null)

const defaultForm = () => ({
  name: '',
  condition_type: 'weight_change',
  condition_params: { days: 7, weight_kg: 2 },
  reward_type: 'text',
  reward_content: '',
  reward_image: null,
  grant_mode: 'auto',
  target_users: 'all',
  is_active: true
})

const form = ref(defaultForm())

const fetchRules = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.get('/api/admin/reward-rules', {
      headers: { Authorization: `Bearer ${token}` }
    })
    rules.value = res.data
  } catch (err) { console.error(err) }
}

const openCreate = () => {
  isEditing.value = false
  editingId.value = null
  form.value = defaultForm()
  selectedFile.value = null
  showModal.value = true
}

const openEdit = (rule) => {
  isEditing.value = true
  editingId.value = rule.id
  form.value = {
    name: rule.name,
    condition_type: rule.condition_type,
    condition_params: { ...rule.condition_params },
    reward_type: rule.reward_type,
    reward_content: rule.reward_content || '',
    reward_image: rule.reward_image || null,
    grant_mode: rule.grant_mode,
    target_users: typeof rule.target_users === 'string' ? rule.target_users : rule.target_users.join(','),
    is_active: rule.is_active
  }
  selectedFile.value = null
  showModal.value = true
}

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) selectedFile.value = file
}

const handleSave = async () => {
  errorMsg.value = ''
  if (!form.value.name) { errorMsg.value = '请输入规则名称'; return }
  saving.value = true
  try {
    const token = localStorage.getItem('admin_token')
    const headers = { Authorization: `Bearer ${token}` }

    let targetUsers = form.value.target_users
    if (targetUsers && targetUsers !== 'all') {
      targetUsers = targetUsers.split(',').map(s => s.trim()).filter(Boolean)
    }

    const payload = {
      name: form.value.name,
      condition_type: form.value.condition_type,
      condition_params: form.value.condition_params,
      reward_type: form.value.reward_type,
      reward_content: form.value.reward_content,
      grant_mode: form.value.grant_mode,
      target_users: targetUsers,
      is_active: form.value.is_active
    }

    if (isEditing.value) {
      await axios.put(`/api/admin/reward-rules/${editingId.value}`, payload, { headers })
    } else {
      await axios.post('/api/admin/reward-rules', payload, { headers })
      if (selectedFile.value && form.value.reward_type === 'image') {
        const fd = new FormData()
        fd.append('image', selectedFile.value)
        // 上传图片可以在创建后单独调用
      }
    }

    showModal.value = false
    await fetchRules()
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '保存失败'
  } finally { saving.value = false }
}

const handleDelete = async (rule) => {
  if (!confirm('确认删除此规则？')) return
  try {
    const token = localStorage.getItem('admin_token')
    await axios.delete(`/api/admin/reward-rules/${rule.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    await fetchRules()
  } catch (err) { alert('删除失败') }
}

onMounted(fetchRules)
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

.actions { display: flex; gap: 4px; }

.btn-delete { background: #fff5f5; color: var(--color-danger); }
.btn-delete:hover { background: var(--color-danger); color: white; }

.tag-active { background: #d4edda; color: #155724; padding: 2px 10px; border-radius: 12px; font-size: 12px; }
.tag-inactive { background: #f8d7da; color: #721c24; padding: 2px 10px; border-radius: 12px; font-size: 12px; }

.form-group { margin-bottom: var(--spacing-md); }

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.error-msg { color: var(--color-danger); font-size: var(--font-size-xs); margin-bottom: var(--spacing-sm); }
</style>
