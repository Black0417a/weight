<template>
  <div class="dashboard">
    <div class="today-card card">
      <p class="today-label">{{ isToday ? '今日体重' : '最近体重' }}</p>
      <p class="today-date">{{ displayDate }}</p>
      <div class="today-weight-row">
        <span class="today-weight">{{ displayWeight }}</span>
        <span class="today-unit">kg</span>
      </div>
      <div v-if="bmi !== null" class="today-bmi-row">
        <span class="bmi-label">BMI</span>
        <span class="bmi-value">{{ bmi }}</span>
        <span class="bmi-cat">{{ bmiCategory }}</span>
      </div>
      <div v-if="goal" class="today-goal-row">
        <span class="goal-hint">🎯 目标 {{ goal.target_weight }}kg</span>
        <span v-if="displayWeight !== '--'" class="goal-remain">
          还差 {{ (displayWeight - goal.target_weight).toFixed(1) }}kg
        </span>
      </div>
      <router-link v-else to="/goal" class="set-goal-link">设置目标体重 →</router-link>

      <div class="quick-record">
        <div class="quick-input-row">
          <input
            type="number"
            v-model="quickWeight"
            step="0.1"
            min="1"
            max="500"
            class="quick-input"
            placeholder="记录今日体重"
            @keyup.enter="handleQuickRecord"
          />
          <button class="btn btn-primary quick-btn" :disabled="saving" @click="handleQuickRecord">
            {{ saving ? '...' : '记录' }}
          </button>
        </div>
        <p v-if="quickError" class="quick-error">{{ quickError }}</p>
        <p v-if="quickSuccess" class="quick-success">{{ quickSuccess }}</p>
      </div>
    </div>

    <div class="card calendar-card">
      <div class="calendar-header">
        <button class="nav-btn" @click="prevMonth">‹</button>
        <span class="calendar-title">{{ calendarTitle }}</span>
        <button class="nav-btn" @click="nextMonth">›</button>
      </div>
      <div class="calendar-weekdays">
        <span v-for="d in weekdays" :key="d" class="weekday">{{ d }}</span>
      </div>
      <div class="calendar-grid">
        <div
          v-for="(day, idx) in calendarDays"
          :key="idx"
          class="calendar-day"
          :class="{
            'empty': !day.date,
            'today': day.isToday,
            'has-record': day.weight,
            'other-month': day.otherMonth
          }"
        >
          <span v-if="day.date" class="day-num">{{ day.day }}</span>
          <span v-if="day.weight" class="day-weight">{{ day.weight }}</span>
        </div>
      </div>
    </div>

    <div v-if="showRewardModal" class="modal-overlay" @click.self="closeRewardModal">
      <div class="reward-modal-content">
        <div class="reward-modal-icon">🎉</div>
        <h3 class="reward-modal-title">
          <template v-if="activeReward.condition_type === 'weight_change'">
            🏆 体重变化奖励达成！
          </template>
          <template v-else>
            恭喜！目标达成！
          </template>
        </h3>
        <p class="reward-modal-text">
          <template v-if="activeReward.condition_type === 'weight_change'">
            你成功减重了 <strong>{{ activeReward.target_weight }}kg</strong>，
            当前体重 <strong>{{ activeReward.weight_value }}kg</strong>
          </template>
          <template v-else>
            你当前的体重 <strong>{{ activeReward.weight_value }}kg</strong> 
            已达到目标 <strong>{{ activeReward.target_weight }}kg</strong>！
          </template>
        </p>
        <div v-if="activeReward.reward_type === 'image' && activeReward.reward_image" class="reward-image-wrap">
          <img :src="getImageUrl(activeReward.reward_image)" class="reward-image" alt="奖励" />
        </div>
        <div v-if="activeReward.reward_content" class="reward-content-box">
          {{ activeReward.reward_content }}
        </div>
        <button class="btn btn-primary reward-close-btn" @click="closeRewardModal">
          太棒了！
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import request from '@/utils/request'
import { getBeijingToday, formatDateStr } from '@/utils/date'

const todayStr = getBeijingToday()
const [todayY, todayM] = todayStr.split('-').map(Number)
const records = ref([])
const goal = ref(null)
const viewYear = ref(todayY)
const viewMonth = ref(todayM - 1)

const quickWeight = ref('')
const quickError = ref('')
const quickSuccess = ref('')
const saving = ref(false)

const showRewardModal = ref(false)
const activeReward = ref({})

const userProfile = ref({})

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const isToday = computed(() => {
  if (records.value.length === 0) return false
  return records.value[records.value.length - 1].record_date === todayStr
})

const displayDate = computed(() => {
  if (records.value.length === 0) return todayStr
  return records.value[records.value.length - 1].record_date
})

const displayWeight = computed(() => {
  if (records.value.length === 0) return '--'
  return records.value[records.value.length - 1].weight
})

const latestWeight = computed(() => {
  if (records.value.length === 0) return null
  return parseFloat(records.value[records.value.length - 1].weight)
})

const bmi = computed(() => {
  const h = userProfile.value.height
  const w = latestWeight.value
  if (!h || !w) return null
  return (w / ((h / 100) ** 2)).toFixed(1)
})

const bmiCategory = computed(() => {
  const val = parseFloat(bmi.value)
  if (isNaN(val)) return ''
  if (val < 18.5) return '偏瘦'
  if (val < 24) return '正常'
  if (val < 28) return '偏胖'
  return '肥胖'
})

const calendarTitle = computed(() => {
  return `${viewYear.value}年${viewMonth.value + 1}月`
})

const weightMap = computed(() => {
  const map = {}
  records.value.forEach(r => {
    map[r.record_date] = r.weight
  })
  return map
})

const calendarDays = computed(() => {
  const year = viewYear.value
  const month = viewMonth.value
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  const startWeekday = firstDay.getDay()

  const days = []

  for (let i = 0; i < startWeekday; i++) {
    const prevDate = new Date(year, month, -startWeekday + i + 1)
    const dateStr = formatDateStr(prevDate.getFullYear(), prevDate.getMonth(), prevDate.getDate())
    days.push({
      date: prevDate,
      dateStr,
      day: prevDate.getDate(),
      otherMonth: true,
      isToday: dateStr === todayStr,
      weight: weightMap.value[dateStr]
    })
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(year, month, d)
    const dateStr = formatDateStr(year, month, d)
    days.push({
      date,
      dateStr,
      day: d,
      otherMonth: false,
      isToday: dateStr === todayStr,
      weight: weightMap.value[dateStr]
    })
  }

  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const nextDate = new Date(year, month + 1, i)
    const dateStr = formatDateStr(nextDate.getFullYear(), nextDate.getMonth(), nextDate.getDate())
    days.push({
      date: nextDate,
      dateStr,
      day: nextDate.getDate(),
      otherMonth: true,
      isToday: dateStr === todayStr,
      weight: weightMap.value[dateStr]
    })
  }

  return days
})

const prevMonth = () => {
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value--
  } else {
    viewMonth.value--
  }
}

const nextMonth = () => {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value++
  } else {
    viewMonth.value++
  }
}

const handleQuickRecord = async () => {
  quickError.value = ''
  quickSuccess.value = ''

  if (!quickWeight.value) {
    quickError.value = '请输入体重'
    return
  }

  const w = parseFloat(quickWeight.value)
  if (w <= 0 || w > 500) {
    quickError.value = '体重数值不合法'
    return
  }

  saving.value = true
  try {
    const res = await request.post('/weights', {
      weight: w,
      record_date: todayStr
    })

    quickSuccess.value = '记录成功！'
    quickWeight.value = ''
    await fetchData()

    if (res.rewards && res.rewards.length > 0) {
      activeReward.value = res.rewards[0]
      showRewardModal.value = true
    }

    setTimeout(() => {
      quickSuccess.value = ''
    }, 2000)
  } catch (err) {
    quickError.value = err.response?.data?.error || '记录失败'
  } finally {
    saving.value = false
  }
}

const fetchData = async () => {
  try {
    const startDate = new Date(viewYear.value, viewMonth.value - 1, 1)
    const endDate = new Date(viewYear.value, viewMonth.value + 2, 0)
    const start = formatDateStr(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
    const end = formatDateStr(endDate.getFullYear(), endDate.getMonth(), endDate.getDate())

    const [res, goalRes, profileRes] = await Promise.all([
      request.get('/weights', { params: { start_date: start, end_date: end } }),
      request.get('/goal'),
      request.get('/auth/profile')
    ])
    records.value = res
    if (goalRes.target_weight) {
      goal.value = goalRes
    }
    userProfile.value = profileRes
    localStorage.setItem('user_info', JSON.stringify(profileRes))
  } catch (err) {
    console.error(err)
  }
}

watch([viewYear, viewMonth], fetchData)

onMounted(fetchData)

const closeRewardModal = async () => {
  showRewardModal.value = false
  if (activeReward.value.id) {
    try {
      await request.put(`/rewards/${activeReward.value.id}/read`)
    } catch (err) {
      console.error(err)
    }
  }
  activeReward.value = {}
}

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return path
}
</script>

<style scoped>
.today-card {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
  background: linear-gradient(135deg, #fff5f5, #ffe8e8);
  border-radius: var(--radius-xl);
  margin-bottom: var(--spacing-lg);
}

.today-label {
  font-size: var(--font-size-sm);
  color: var(--text-light);
  margin-bottom: var(--spacing-xs);
}

.today-date {
  font-size: var(--font-size-xs);
  color: var(--text-light);
  margin-bottom: var(--spacing-md);
}

.today-weight-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: var(--spacing-sm);
}

.today-weight {
  font-size: 56px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.today-unit {
  font-size: var(--font-size-xl);
  color: var(--text-light);
}

.today-goal-row {
  margin-top: var(--spacing-md);
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.today-bmi-row {
  margin-top: var(--spacing-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.bmi-label {
  color: var(--text-light);
}

.bmi-value {
  font-weight: 700;
  color: var(--color-secondary);
  font-size: var(--font-size-lg);
}

.bmi-cat {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
}

.goal-remain {
  color: var(--color-secondary);
  font-weight: 600;
}

.set-goal-link {
  display: inline-block;
  margin-top: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  text-decoration: none;
}

.quick-record {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid rgba(255,107,107,0.2);
}

.quick-input-row {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
}

.quick-input {
  width: 140px;
  padding: 10px 14px;
  border: 2px solid #ffd4d4;
  border-radius: var(--radius-full);
  font-size: var(--font-size-base);
  text-align: center;
  background: white;
  transition: border-color 0.2s ease;
}

.quick-input:focus {
  border-color: var(--color-primary);
  outline: none;
}

.quick-input::placeholder {
  color: #ccc;
  font-size: var(--font-size-sm);
}

.quick-btn {
  padding: 10px 20px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
}

.quick-error {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-sm);
}

.quick-success {
  color: var(--color-success);
  font-size: var(--font-size-xs);
  margin-top: var(--spacing-sm);
}

.calendar-card {
  padding: var(--spacing-md);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  padding: 0 var(--spacing-sm);
}

.calendar-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.nav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-primary);
  color: var(--color-primary);
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:hover {
  background: var(--color-primary);
  color: white;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: var(--spacing-sm);
}

.weekday {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-light);
  padding: var(--spacing-xs) 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  min-height: 48px;
}

.calendar-day.empty {
  background: transparent;
}

.calendar-day.other-month {
  opacity: 0.4;
}

.calendar-day.today {
  background: var(--color-primary);
}

.calendar-day.today .day-num,
.calendar-day.today .day-weight {
  color: white;
}

.calendar-day.has-record {
  background: #ffe8e8;
}

.calendar-day.today.has-record {
  background: var(--color-primary);
}

.day-num {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1;
}

.day-weight {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  margin-top: 2px;
}

@media screen and (max-width: 767px) {
  .today-card { padding: var(--spacing-lg); }
  .today-weight { font-size: 44px; }
  .quick-input { width: 120px; padding: 8px 12px; font-size: var(--font-size-sm); }
  .quick-btn { padding: 8px 16px; }
  .calendar-day { min-height: 40px; }
  .day-num { font-size: 11px; }
  .day-weight { font-size: 10px; }
}

.reward-modal-content {
    background: linear-gradient(135deg, #fff9e6, #fff3cd);
    border-radius: 24px;
    padding: 40px 32px 32px;
    text-align: center;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    animation: rewardPop 0.4s ease;
}

@keyframes rewardPop {
    0% { transform: scale(0.5); opacity: 0; }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
}

.reward-modal-icon {
    font-size: 64px;
    margin-bottom: 12px;
}

.reward-modal-title {
    font-size: 22px;
    font-weight: 700;
    color: #333;
    margin-bottom: 12px;
}

.reward-modal-text {
    font-size: 15px;
    color: #666;
    line-height: 1.6;
    margin-bottom: 16px;
}

.reward-modal-text strong {
    color: var(--color-primary);
}

.reward-image-wrap {
    margin-bottom: 16px;
}

.reward-image {
    max-width: 100%;
    max-height: 200px;
    border-radius: 12px;
}

.reward-content-box {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    font-size: 15px;
    color: #444;
    line-height: 1.7;
    white-space: pre-wrap;
}

.reward-close-btn {
    padding: 12px 40px;
    border-radius: 24px;
    font-size: 16px;
    font-weight: 600;
}
</style>
