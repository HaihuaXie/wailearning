import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import api, { http } from '@/api'
import { normalizeSystemSettings } from '@/utils/branding'

const cachedSystemSettings = normalizeSystemSettings(
  JSON.parse(localStorage.getItem('system_settings') || 'null')
)

if (cachedSystemSettings) {
  localStorage.setItem('system_settings', JSON.stringify(cachedSystemSettings))
}

const cachedSelectedCourse = JSON.parse(localStorage.getItem('selected_course') || 'null')

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const systemSettings = ref(cachedSystemSettings)
  const selectedCourse = ref(cachedSelectedCourse)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  const isClassTeacher = computed(() => userInfo.value?.role === 'class_teacher')
  const isTeacher = computed(() => userInfo.value?.role === 'teacher')
  const isStudent = computed(() => userInfo.value?.role === 'student')
  const classId = computed(() => userInfo.value?.class_id)
  const canManageTeaching = computed(() => ['admin', 'class_teacher', 'teacher'].includes(userInfo.value?.role))

  function setSelectedCourse(course) {
    selectedCourse.value = course || null
    if (course) {
      localStorage.setItem('selected_course', JSON.stringify(course))
    } else {
      localStorage.removeItem('selected_course')
    }
  }

  function clearSelectedCourse() {
    setSelectedCourse(null)
  }

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const data = await api.auth.login(formData)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)

    const userData = await api.auth.getCurrentUser()
    userInfo.value = userData
    localStorage.setItem('user', JSON.stringify(userData))

    await fetchSystemSettings()

    return userData
  }

  async function fetchSystemSettings() {
    try {
      const data = await http.get('/settings/public')
      const normalizedSettings = normalizeSystemSettings(data)
      systemSettings.value = normalizedSettings
      localStorage.setItem('system_settings', JSON.stringify(normalizedSettings))
      document.title = normalizedSettings?.system_name || 'BIMSA-CLASS 管理端'
    } catch (error) {
      console.error('Failed to fetch system settings', error)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    systemSettings.value = null
    selectedCourse.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('system_settings')
    localStorage.removeItem('selected_course')
  }

  return {
    token,
    userInfo,
    systemSettings,
    selectedCourse,
    isLoggedIn,
    isAdmin,
    isClassTeacher,
    isTeacher,
    isStudent,
    classId,
    canManageTeaching,
    login,
    logout,
    fetchSystemSettings,
    setSelectedCourse,
    clearSelectedCourse
  }
})
