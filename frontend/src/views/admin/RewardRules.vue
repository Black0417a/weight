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
            <th>目标用户</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rules" :key="r.id">
            <td>{{ r.name }}</td>
            <td>{{ r.condition_type === 'weight_change' ? '体重变化' : '目标达成' }}</td>
            <td>{{ r.grant_mode === 'auto' ? '自动' : '手动' }}</td>
            <td>{{ formatTargetUsers(r.target_users) }}</td>
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
          <div class="user-select-box">
            <div class="user-select-all">
              <label class="checkbox-item">
                <input type="checkbox" v-model="allSelected" @change="toggleAll" />
                <span>全部用户</span>
              </label>
            </div>
            <div class="user-select-list">
              <label
                v-for="u in allUsers"
                :key="u.id"
                class="checkbox-item"
                :class="{ 'disabled': allSelected }"
              >
                <input
                  type="checkbox"
                  :value="u.id"
                  v-model="selectedUserIds"
                  :disabled="allSelected"
                />
                <span>{{ u.email }}</span>
              </label>
            </div>
            <div v-if="allUsers.length === 0" class="user-select-empty">暂无用户</div>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'

const rules = ref([])
const allUsers = ref([])
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const errorMsg = ref('')
const selectedFile = ref(null)
const selectedUserIds = ref([])
const allSelected = ref(true)

const defaultForm = () => ({
  name: '',
  condition_type: 'weight_change',
  condition_params: { days: 7, weight_kg: 2 },
  reward_type: 'text',
  reward_content: '',
  reward_image: null,
  grant_mode: 'auto',
  is_active: true
})

const form = ref(defaultForm())

const formatTargetUsers = (target) => {
  if (!target || target === 'all') return '全部用户'
  if (Array.isArray(target)) {
    if (target.length === 0) return '无'
    const names = target.map(id => {
      const u = allUsers.value.find(u => u.id === Number(id))
      return u ? u.email : `#${id}`
    })
    return names.join(', ')
  }
  return String(target)
}

const fetchUsers = async () => {
  try {
    const res = await request.get('/admin/users', {
      params: { per_page: 1000 }
    })
    allUsers.value = res.users
  } catch (err) { console.error(err) }
}

const fetchRules = async () => {
  try {
    const res = await request.get('/admin/reward-rules')
    rules.value = res
  } catch (err) { console.error(err) }
}

const openCreate = () => {
  isEditing.value = false
  editingId.value = null
  form.value = defaultForm()
  selectedFile.value = null
  allSelected.value = true
  selectedUserIds.value = []
  showModal.value = true
}

const openEdit = async (rule) => {
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
    is_active: rule.is_active
  }
  selectedFile.value = null

  const target = rule.target_users
  if (target === 'all' || (Array.isArray(target) && target.length === 0)) {
    allSelected.value = true
    selectedUserIds.value = []
  } else if (Array.isArray(target)) {
    allSelected.value = false
    selectedUserIds.value = target.map(Number)
  } else {
    allSelected.value = true
    selectedUserIds.value = []
  }

  showModal.value = true
}

const toggleAll = () => {
  if (allSelected.value) {
    selectedUserIds.value = []
  }
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
    let targetUsers = 'all'
    if (!allSelected.value) {
      targetUsers = selectedUserIds.value.map(String)
      if (targetUsers.length === 0) {
        targetUsers = 'all'
      }
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
      await request.put(`/admin/reward-rules/${editingId.value}`, payload)
    } else {
      await request.post('/admin/reward-rules', payload)
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
    await request.delete(`/admin/reward-rules/${rule.id}`)
    await fetchRules()
  } catch (err) { alert('删除失败') }
}

onMounted(() => {
  fetchUsers()
  fetchRules()
})
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

.user-select-box {
  border: 2px solid #ffe0e0;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.user-select-all {
  padding: 10px 14px;
  background: var(--bg-primary);
  border-bottom: 1px solid #ffe0e0;
}

.user-select-list {
  max-height: 180px;
  overflow-y: auto;
  padding: 4px 0;
}

.user-select-empty {
  padding: 16px;
  text-align: center;
  color: var(--text-light);
  font-size: var(--font-size-sm);
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  transition: background 0.2s ease;
}

.checkbox-item:hover {
  background: var(--bg-hover);
}

.checkbox-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.checkbox-item.disabled:hover {
  background: transparent;
}

.checkbox-item input[type="checkbox"] {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}

.checkbox-item span {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
