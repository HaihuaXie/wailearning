import { formatScheduleValue } from '@/utils/courseSchedule'

const pad = value => `${value}`.padStart(2, '0')

export const normalizeCourseBoundaryDate = value => {
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

export const normalizeCourseDateField = value => {
  const normalizedDate = normalizeCourseBoundaryDate(value)

  if (!normalizedDate) {
    return ''
  }

  return `${normalizedDate.getFullYear()}-${pad(normalizedDate.getMonth() + 1)}-${pad(normalizedDate.getDate())}`
}

export const serializeCourseDateField = (value, boundary) => {
  const normalizedDate = normalizeCourseDateField(value)

  if (!normalizedDate) {
    return ''
  }

  return boundary === 'end'
    ? `${normalizedDate}T23:59:59`
    : `${normalizedDate}T00:00:00`
}

export const createEmptyCourseTime = () => ({
  weekly_schedule: '',
  course_start_at: '',
  course_end_at: ''
})

const hasAnyCourseTimeValue = courseTime =>
  Boolean(courseTime?.weekly_schedule || courseTime?.course_start_at || courseTime?.course_end_at)

const hasCompleteCourseTime = courseTime =>
  Boolean(courseTime?.weekly_schedule && courseTime?.course_start_at && courseTime?.course_end_at)

const normalizeCourseTimeItem = courseTime => ({
  weekly_schedule: `${courseTime?.weekly_schedule || ''}`.trim(),
  course_start_at: normalizeCourseDateField(courseTime?.course_start_at),
  course_end_at: normalizeCourseDateField(courseTime?.course_end_at)
})

export const normalizeEditableCourseTimes = source => {
  const rawItems = Array.isArray(source)
    ? source
    : Array.isArray(source?.course_times) && source.course_times.length
      ? source.course_times
      : [source]

  return rawItems
    .map(normalizeCourseTimeItem)
    .filter(hasAnyCourseTimeValue)
}

export const resolveCourseTimes = source =>
  normalizeEditableCourseTimes(source).filter(hasCompleteCourseTime)

export const serializeCourseTimesPayload = courseTimes =>
  resolveCourseTimes(courseTimes).map(item => ({
    weekly_schedule: item.weekly_schedule,
    course_start_at: serializeCourseDateField(item.course_start_at, 'start'),
    course_end_at: serializeCourseDateField(item.course_end_at, 'end')
  }))

const formatDisplayDate = value => {
  const normalizedDate = normalizeCourseBoundaryDate(value)

  if (!normalizedDate) {
    return ''
  }

  return normalizedDate.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

export const formatCourseTimeDateRange = (startAt, endAt) => {
  const startLabel = formatDisplayDate(startAt)
  const endLabel = formatDisplayDate(endAt)

  if (startLabel && endLabel) {
    return `${startLabel} - ${endLabel}`
  }

  return startLabel || endLabel || ''
}

export const formatCourseTimeEntry = courseTime => {
  const rangeLabel = formatCourseTimeDateRange(courseTime?.course_start_at, courseTime?.course_end_at)
  const scheduleLabel = formatScheduleValue(courseTime?.weekly_schedule) || courseTime?.weekly_schedule || ''

  if (rangeLabel && scheduleLabel) {
    return `${rangeLabel}：${scheduleLabel}`
  }

  return rangeLabel || scheduleLabel || ''
}

export const formatCourseTimes = (source, { joiner = '；' } = {}) =>
  resolveCourseTimes(source)
    .map(formatCourseTimeEntry)
    .filter(Boolean)
    .join(joiner)

export const getCourseTimeDateBounds = source => {
  const courseTimes = resolveCourseTimes(source)

  if (!courseTimes.length) {
    return { startDate: null, endDate: null }
  }

  return courseTimes.reduce(
    (bounds, item) => {
      const startDate = normalizeCourseBoundaryDate(item.course_start_at)
      const endDate = normalizeCourseBoundaryDate(item.course_end_at)

      if (startDate && (!bounds.startDate || startDate < bounds.startDate)) {
        bounds.startDate = startDate
      }

      if (endDate && (!bounds.endDate || endDate > bounds.endDate)) {
        bounds.endDate = endDate
      }

      return bounds
    },
    { startDate: null, endDate: null }
  )
}
