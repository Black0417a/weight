<template>
  <div class="chart-page">
    <h2 class="page-title">📊 体重趋势</h2>
    <div class="card">
      <div class="chart-controls">
        <div class="control-group">
          <button
            v-for="t in chartTypes"
            :key="t.value"
            class="btn"
            :class="chartType === t.value ? 'btn-primary' : 'btn-secondary'"
            @click="chartType = t.value"
          >{{ t.label }}</button>
        </div>
        <div class="control-group">
          <button
            v-for="p in periods"
            :key="p.value"
            class="btn"
            :class="period === p.value ? 'btn-primary' : 'btn-secondary'"
            @click="period = p.value"
          >{{ p.label }}</button>
        </div>
      </div>
      <div ref="chartRef" class="chart-container"></div>
      <div v-if="records.length === 0 && !loading" class="empty-state">
        <div class="empty-state-icon">📈</div>
        <p class="empty-state-text">暂无体重数据，快去记录吧</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const chartRef = ref(null)
let chartInstance = null

const records = ref([])
const goal = ref(null)
const loading = ref(true)

const chartType = ref('line')
const period = ref('month')

const chartTypes = [
  { label: '📈 折线图', value: 'line' },
  { label: '📊 柱状图', value: 'bar' }
]

const periods = [
  { label: '周', value: 'week' },
  { label: '月', value: 'month' },
  { label: '季度', value: 'quarter' }
]

const getDateRange = () => {
  const today = new Date()
  let startDate = new Date(today)
  const endDate = today.toISOString().split('T')[0]

  if (period.value === 'week') {
    startDate.setDate(today.getDate() - 7)
  } else if (period.value === 'month') {
    startDate.setMonth(today.getMonth() - 1)
  } else {
    startDate.setMonth(today.getMonth() - 3)
  }

  return { start: startDate.toISOString().split('T')[0], end: endDate }
}

const fetchData = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('user_token')
    const headers = { Authorization: `Bearer ${token}` }
    const range = getDateRange()

    const [weightRes, goalRes] = await Promise.all([
      axios.get('/api/weights', { params: { start_date: range.start, end_date: range.end }, headers }),
      axios.get('/api/goal', { headers })
    ])
    records.value = weightRes.data
    if (goalRes.data.target_weight) {
      goal.value = goalRes.data
    }
  } catch (err) {
    console.error('获取数据失败', err)
  } finally {
    loading.value = false
    nextTick(renderChart)
  }
}

const renderChart = () => {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  if (records.value.length === 0) {
    chartInstance.setOption({})
    return
  }

  const dates = records.value.map(r => r.record_date)
  const weights = records.value.map(r => r.weight)

  const series = [{
    name: '体重',
    type: chartType.value,
    data: weights,
    smooth: true,
    lineStyle: { color: '#ff6b6b', width: 3 },
    itemStyle: { color: '#ff6b6b' },
    areaStyle: chartType.value === 'line' ? {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(255,107,107,0.3)' },
        { offset: 1, color: 'rgba(255,107,107,0.02)' }
      ])
    } : undefined
  }]

  if (goal.value && goal.value.target_weight) {
    series.push({
      name: '目标体重',
      type: 'line',
      data: Array(weights.length).fill(goal.value.target_weight),
      lineStyle: { color: '#ffa94d', type: 'dashed', width: 2 },
      itemStyle: { color: '#ffa94d' },
      symbol: 'none'
    })
  }

  chartInstance.setOption({
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#eee' } },
      axisLabel: { color: '#999', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: 'kg',
      nameTextStyle: { color: '#999' },
      axisLabel: { color: '#999' },
      splitLine: { lineStyle: { color: '#f5f5f5' } }
    },
    series,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#ffe0e0',
      textStyle: { color: '#333' }
    }
  }, true)
}

watch([chartType, period], () => { fetchData() })

onMounted(() => { fetchData() })
</script>

<style scoped>
.chart-controls {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  gap: var(--spacing-sm);
}

.chart-container {
  width: 100%;
  height: 400px;
}

@media screen and (max-width: 767px) {
  .chart-container { height: 300px; }
  .chart-controls { gap: var(--spacing-sm); }
  .control-group .btn { padding: 6px 12px; font-size: var(--font-size-xs); }
}
</style>
