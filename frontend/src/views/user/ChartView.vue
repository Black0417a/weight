<template>
  <div class="chart-page">
    <h2 class="page-title">体重趋势</h2>
    <div class="card">
      <div class="chart-controls">
        <div class="control-group">
          <button
            v-for="t in chartTypes"
            :key="t.value"
            class="btn btn-sm"
            :class="chartType === t.value ? 'btn-primary' : 'btn-secondary'"
            @click="switchChartType(t.value)"
          >{{ t.label }}</button>
        </div>
        <div class="control-group">
          <button
            v-for="p in periods"
            :key="p.value"
            class="btn btn-sm"
            :class="period === p.value ? 'btn-primary' : 'btn-secondary'"
            @click="switchPeriod(p.value)"
          >{{ p.label }}</button>
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
      </div>

      <div v-else-if="records.length === 0" class="empty-state">
        <div class="empty-state-icon">📈</div>
        <p class="empty-state-text">暂无体重数据，去记录吧</p>
      </div>

      <div v-else>
        <div ref="chartRef" class="chart-container"></div>
        <div class="chart-legend" v-if="goal">
          <span class="legend-item"><span class="legend-dot weight"></span>体重</span>
          <span class="legend-item"><span class="legend-dot goal"></span>目标 {{ goal.target_weight }}kg</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import request from '@/utils/request'
import * as echarts from 'echarts'
import { getBeijingToday, formatDateStr } from '@/utils/date'

const chartRef = ref(null)
let chartInstance = null

const records = ref([])
const goal = ref(null)
const loading = ref(true)

const chartType = ref('line')
const period = ref('month')

const chartTypes = [
  { label: '折线', value: 'line' },
  { label: '柱状', value: 'bar' }
]

const periods = [
  { label: '周', value: 'week' },
  { label: '月', value: 'month' },
  { label: '季度', value: 'quarter' }
]

const computeDateRange = (p) => {
  const beijingToday = getBeijingToday()
  const [y, m, d] = beijingToday.split('-').map(Number)
  const startDate = new Date(y, m - 1, d)

  if (p === 'week') {
    startDate.setDate(startDate.getDate() - 7)
  } else if (p === 'month') {
    startDate.setMonth(startDate.getMonth() - 1)
  } else if (p === 'quarter') {
    startDate.setMonth(startDate.getMonth() - 3)
  }

  const start = formatDateStr(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
  return { start, end: beijingToday }
}

const fetchData = async () => {
  loading.value = true
  records.value = []
  try {
    const range = computeDateRange(period.value)

    const [weightRes, goalRes] = await Promise.all([
      request.get('/weights', { params: { start_date: range.start, end_date: range.end } }),
      request.get('/goal')
    ])

    records.value = weightRes
    if (goalRes.target_weight) {
      goal.value = goalRes
    } else {
      goal.value = null
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
    await nextTick()
    renderChart()
  }
}

const switchChartType = (type) => {
  chartType.value = type
  nextTick(renderChart)
}

const switchPeriod = (p) => {
  period.value = p
  fetchData()
}

const disposeChart = () => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
}

const isMobile = () => window.innerWidth <= 767

const renderChart = () => {
  if (!chartRef.value) return

  disposeChart()
  chartInstance = echarts.init(chartRef.value)

  if (records.value.length === 0) {
    chartInstance.setOption({
      title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#ccc', fontSize: 14 } }
    })
    return
  }

  const dates = records.value.map(r => r.record_date)
  const weights = records.value.map(r => r.weight)
  const mobile = isMobile()

  const series = [{
    name: '体重',
    type: chartType.value,
    data: weights,
    smooth: true,
    lineStyle: { color: '#ff6b6b', width: mobile ? 2 : 3 },
    itemStyle: { color: '#ff6b6b' },
    barWidth: mobile ? '50%' : '60%',
    showSymbol: !mobile || dates.length <= 10,
    symbolSize: mobile ? 4 : 6,
    areaStyle: chartType.value === 'line' ? {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(255,107,107,0.2)' },
        { offset: 1, color: 'rgba(255,107,107,0.02)' }
      ])
    } : undefined
  }]

  if (goal.value && goal.value.target_weight) {
    series.push({
      name: '目标',
      type: 'line',
      data: Array(weights.length).fill(goal.value.target_weight),
      lineStyle: { color: '#ffa94d', type: 'dashed', width: mobile ? 1 : 2 },
      itemStyle: { color: '#ffa94d' },
      symbol: 'none'
    })
  }

  const yMin = Math.floor(Math.min(...weights, goal.value ? goal.value.target_weight : Infinity) - 3)
  const yMax = Math.ceil(Math.max(...weights, goal.value ? goal.value.target_weight : -Infinity) + 3)

  const dataCount = dates.length
  let xLabelInterval = 0
  let xLabelRotate = 0
  if (mobile) {
    xLabelInterval = dataCount > 10 ? Math.floor(dataCount / 6) : 0
    xLabelRotate = dataCount > 15 ? 30 : 0
  } else {
    xLabelInterval = dataCount > 15 ? Math.floor(dataCount / 10) : 0
    xLabelRotate = dataCount > 20 ? 30 : 0
  }

  chartInstance.setOption({
    grid: {
      top: mobile ? 8 : 12,
      right: mobile ? 8 : 12,
      bottom: mobile ? 20 : 28,
      left: mobile ? 36 : 42
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#eee' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#999',
        fontSize: mobile ? 9 : 11,
        interval: xLabelInterval,
        rotate: xLabelRotate
      }
    },
    yAxis: {
      type: 'value',
      min: yMin,
      max: yMax,
      name: 'kg',
      nameTextStyle: { color: '#999', fontSize: mobile ? 9 : 11, padding: [0, 0, 0, -20] },
      axisLabel: { color: '#999', fontSize: mobile ? 9 : 11 },
      splitLine: { lineStyle: { color: '#f5f5f5' } },
      axisTick: { show: false },
      axisLine: { show: false }
    },
    series,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#ffe0e0',
      textStyle: { color: '#333', fontSize: mobile ? 12 : 13 },
      confine: true
    }
  })
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
    renderChart()
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeChart()
})

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.chart-controls {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  gap: 4px;
}

.control-group .btn-sm {
  padding: 6px 14px;
  font-size: var(--font-size-xs);
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid #fef0f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.legend-dot.weight {
  background: #ff6b6b;
}

.legend-dot.goal {
  background: #ffa94d;
}

@media screen and (max-width: 767px) {
  .chart-controls {
    gap: var(--spacing-sm);
    justify-content: center;
  }

  .control-group .btn-sm {
    padding: 4px 10px;
    font-size: 11px;
  }

  .chart-container {
    height: 240px;
  }

  .chart-legend {
    gap: var(--spacing-md);
  }

  .legend-item {
    font-size: 11px;
  }
}
</style>
