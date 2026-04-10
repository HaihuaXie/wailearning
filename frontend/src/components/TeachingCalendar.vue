<template>
  <div class="teaching-calendar">
    <div class="calendar-toolbar">
      <div class="calendar-summary">
        <span>教学周期：{{ courseRangeLabel }}</span>
        <span>本月上课 {{ visibleMonthStats.classDays }} 天</span>
        <span>本月假期 {{ visibleMonthStats.holidayDays }} 天</span>
      </div>
      <div class="calendar-legend">
        <span class="legend-item">
          <i class="legend-dot legend-dot-class"></i>
          上课日
        </span>
        <span class="legend-item">
          <i class="legend-dot legend-dot-holiday"></i>
          法定假期
        </span>
      </div>
    </div>

    <el-alert
      v-if="hasUnsupportedSchedule"
      type="warning"
      :closable="false"
      class="calendar-alert"
    >
      当前课程的“每周时间”为旧版手填格式，暂时无法准确生成教学日历。请在课程管理里改成结构化课表时间后查看。
    </el-alert>

    <el-empty
      v-else-if="!hasRenderableCalendar"
      description="请先完善课程的起始日期、结束日期和每周时间。"
    />

    <el-calendar v-else v-model="calendarDate" class="calendar-panel">
      <template #date-cell="{ data }">
        <div
          class="calendar-cell"
          :class="{
            'is-outside': !resolveCellMeta(data.day).inRange,
            'is-holiday': Boolean(resolveCellMeta(data.day).holiday),
            'is-class-day': Boolean(resolveCellMeta(data.day).classDay)
          }"
        >
          <div class="calendar-cell__day">
            {{ Number(data.day.slice(-2)) }}
          </div>
          <div
            v-if="resolveCellMeta(data.day).holiday"
            class="calendar-pill calendar-pill-holiday"
          >
            {{ resolveCellMeta(data.day).holiday.name }}
          </div>
          <div
            v-else-if="resolveCellMeta(data.day).classDay"
            class="calendar-pill calendar-pill-class"
          >
            上课
          </div>
          <div v-if="resolveCellMeta(data.day).classDay" class="calendar-note">
            {{ resolveCellMeta(data.day).classDay.summary }}
          </div>
          <div
            v-else-if="resolveCellMeta(data.day).holiday?.suspendsClass"
            class="calendar-note calendar-note-muted"
          >
            停课
          </div>
        </div>
      </template>
    </el-calendar>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

import { parseScheduleValue } from '@/utils/courseSchedule'
import { buildHolidayMap } from '@/utils/holidayCalendar'

const props = defineProps({
  course: {
    type: Object,
    default: null
  }
})

const ONE_DAY_MS = 24 * 60 * 60 * 1000
const LEGACY_WEEKDAY_PATTERNS = [
  { value: 1, patterns: [/周一/, /星期一/, /每周一/] },
  { value: 2, patterns: [/周二/, /星期二/, /每周二/] },
  { value: 3, patterns: [/周三/, /星期三/, /每周三/] },
  { value: 4, patterns: [/周四/, /星期四/, /每周四/] },
  { value: 5, patterns: [/周五/, /星期五/, /每周五/] },
  { value: 6, patterns: [/周六/, /星期六/, /每周六/] },
  { value: 7, patterns: [/周日/, /星期日/, /周天/, /星期天/, /每周日/, /每周天/] }
]

const calendarDate = ref(new Date())

const toDateKey = date => {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

const normalizeBoundaryDate = value => {
  if (!value) {
    return null
  }

  if (value instanceof Date) {
    return new Date(value.getFullYear(), value.getMonth(), value.getDate())
  }

  const rawValue = `${value}`.trim()
  const matchedDate = rawValue.match(/^(\d{4})-(\d{2})-(\d{2})/)

  if (matchedDate) {
    return new Date(Number(matchedDate[1]), Number(matchedDate[2]) - 1, Number(matchedDate[3]))
  }

  const parsedDate = new Date(rawValue)
  if (Number.isNaN(parsedDate.getTime())) {
    return null
  }

  return new Date(parsedDate.getFullYear(), parsedDate.getMonth(), parsedDate.getDate())
}

const courseStartDate = computed(() => normalizeBoundaryDate(props.course?.course_start_at))
const courseEndDate = computed(() => normalizeBoundaryDate(props.course?.course_end_at))
const hasValidRange = computed(() =>
  Boolean(courseStartDate.value && courseEndDate.value && courseEndDate.value >= courseStartDate.value)
)

const normalizePeriods = periods => [...new Set(periods)].sort((left, right) => left - right)

const formatPeriodSummary = periods => {
  const sortedPeriods = normalizePeriods(periods)

  if (!sortedPeriods.length) {
    return '常规授课'
  }

  const groups = []
  let groupStart = sortedPeriods[0]
  let groupEnd = sortedPeriods[0]

  for (const period of sortedPeriods.slice(1)) {
    if (period === groupEnd + 1) {
      groupEnd = period
      continue
    }

    groups.push(groupStart === groupEnd ? `第${groupStart}小节` : `第${groupStart}-${groupEnd}小节`)
    groupStart = period
    groupEnd = period
  }

  groups.push(groupStart === groupEnd ? `第${groupStart}小节` : `第${groupStart}-${groupEnd}小节`)
  return groups.join('、')
}

const extractLegacyWeekdays = scheduleText => {
  const normalizedText = `${scheduleText || ''}`.trim()

  if (!normalizedText) {
    return []
  }

  return LEGACY_WEEKDAY_PATTERNS
    .filter(day => day.patterns.some(pattern => pattern.test(normalizedText)))
    .map(day => day.value)
}

const scheduleByDay = computed(() => {
  const parsedSlots = parseScheduleValue(props.course?.weekly_schedule)

  if (parsedSlots.length) {
    return parsedSlots.reduce((map, slot) => {
      const [dayValueRaw, periodValueRaw] = slot.split('-')
      const dayValue = Number(dayValueRaw)
      const periodValue = Number(periodValueRaw)

      if (!map.has(dayValue)) {
        map.set(dayValue, [])
      }

      map.get(dayValue).push(periodValue)
      return map
    }, new Map())
  }

  const legacyWeekdays = extractLegacyWeekdays(props.course?.weekly_schedule)

  return legacyWeekdays.reduce((map, dayValue) => {
    map.set(dayValue, [])
    return map
  }, new Map())
})

const hasSchedule = computed(() => scheduleByDay.value.size > 0)
const hasUnsupportedSchedule = computed(() =>
  Boolean(props.course?.weekly_schedule) && !hasSchedule.value
)
const hasRenderableCalendar = computed(() => hasValidRange.value && hasSchedule.value && !hasUnsupportedSchedule.value)

const holidayMap = computed(() =>
  hasValidRange.value ? buildHolidayMap(courseStartDate.value, courseEndDate.value) : {}
)

const classDateMap = computed(() => {
  if (!hasRenderableCalendar.value) {
    return {}
  }

  const entries = {}
  let currentDate = new Date(courseStartDate.value)

  while (currentDate <= courseEndDate.value) {
    const dayValue = currentDate.getDay() === 0 ? 7 : currentDate.getDay()
    const periods = scheduleByDay.value.get(dayValue) || []
    const dateKey = toDateKey(currentDate)

    if (scheduleByDay.value.has(dayValue) && !holidayMap.value[dateKey]) {
      entries[dateKey] = {
        periods,
        summary: formatPeriodSummary(periods)
      }
    }

    currentDate = new Date(currentDate.getTime() + ONE_DAY_MS)
  }

  return entries
})

const resolveCellMeta = dayString => {
  const cellDate = normalizeBoundaryDate(dayString)

  if (!cellDate) {
    return { inRange: false, holiday: null, classDay: null }
  }

  const inRange = hasValidRange.value && cellDate >= courseStartDate.value && cellDate <= courseEndDate.value
  const dateKey = toDateKey(cellDate)
  const dayValue = cellDate.getDay() === 0 ? 7 : cellDate.getDay()
  const holiday = inRange && holidayMap.value[dateKey]
    ? {
        ...holidayMap.value[dateKey],
        suspendsClass: scheduleByDay.value.has(dayValue)
      }
    : null

  return {
    inRange,
    holiday,
    classDay: inRange ? classDateMap.value[dateKey] || null : null
  }
}

const visibleMonthStats = computed(() => {
  if (!hasRenderableCalendar.value) {
    return { classDays: 0, holidayDays: 0 }
  }

  const targetYear = calendarDate.value.getFullYear()
  const targetMonth = calendarDate.value.getMonth()

  const matchMonth = dateKey => {
    const date = normalizeBoundaryDate(dateKey)
    return date && date.getFullYear() === targetYear && date.getMonth() === targetMonth
  }

  return {
    classDays: Object.keys(classDateMap.value).filter(matchMonth).length,
    holidayDays: Object.keys(holidayMap.value).filter(matchMonth).length
  }
})

const courseRangeLabel = computed(() => {
  if (!hasValidRange.value) {
    return '未设置'
  }

  return `${toDateKey(courseStartDate.value)} 至 ${toDateKey(courseEndDate.value)}`
})

const resolveInitialCalendarDate = course => {
  const startDate = normalizeBoundaryDate(course?.course_start_at)
  const endDate = normalizeBoundaryDate(course?.course_end_at)
  const today = normalizeBoundaryDate(new Date())

  if (startDate && endDate && today >= startDate && today <= endDate) {
    return today
  }

  return startDate || today || new Date()
}

watch(
  () => props.course,
  course => {
    calendarDate.value = resolveInitialCalendarDate(course)
  },
  { immediate: true }
)
</script>

<style scoped>
.teaching-calendar {
  width: 100%;
}

.calendar-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.calendar-summary,
.calendar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  color: #64748b;
  font-size: 13px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.legend-dot-class {
  background: #2563eb;
}

.legend-dot-holiday {
  background: #ef4444;
}

.calendar-alert {
  margin-bottom: 12px;
}

.calendar-panel {
  --el-calendar-border: #e2e8f0;
}

:deep(.el-calendar-table thead th) {
  color: #475569;
  font-weight: 600;
}

:deep(.el-calendar-day) {
  min-height: 108px;
  padding: 0;
}

.calendar-cell {
  height: 100%;
  padding: 10px 10px 8px;
  background: #fff;
  transition: background-color 0.2s ease;
}

.calendar-cell.is-outside {
  background: #f8fafc;
}

.calendar-cell.is-class-day {
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
}

.calendar-cell.is-holiday {
  background: linear-gradient(180deg, #fff1f2 0%, #ffe4e6 100%);
}

.calendar-cell__day {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.calendar-pill {
  display: inline-flex;
  align-items: center;
  margin-top: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.calendar-pill-class {
  color: #1d4ed8;
  background: rgba(37, 99, 235, 0.12);
}

.calendar-pill-holiday {
  color: #b91c1c;
  background: rgba(239, 68, 68, 0.14);
}

.calendar-note {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.5;
  color: #334155;
}

.calendar-note-muted {
  color: #991b1b;
}

@media (max-width: 900px) {
  .calendar-toolbar {
    flex-direction: column;
  }

  :deep(.el-calendar-day) {
    min-height: 92px;
  }
}
</style>
