<template>
  <div class="students-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">学生管理</h1>
        <p class="page-subtitle">{{ pageSubtitle }}</p>
      </div>
      <el-button v-if="!isAdminView" @click="router.push('/courses')">切换课程</el-button>
    </div>

    <el-empty
      v-if="showCourseEmpty"
      description="请先从“我的课程”中选择一门课程。"
    />

    <template v-else>
      <el-alert
        v-if="!isAdminView && selectedCourse"
        :title="selectedCourse.course_type === 'elective' ? '当前为选修课，可移除学生。' : '当前为必修课，系统已自动加入班级全部学生，且不可移除。'"
        :type="selectedCourse.course_type === 'elective' ? 'warning' : 'info'"
        :closable="false"
        class="info-alert"
      />

      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <strong>{{ isAdminView ? '全校学生名单' : '课程学生名单' }}</strong>
              <span class="header-count">共 {{ students.length }} 人</span>
            </div>
          </div>
        </template>

        <el-table :data="students" v-loading="loading">
          <template v-if="isAdminView">
            <el-table-column prop="name" label="姓名" min-width="160" />
            <el-table-column label="性别" width="120">
              <template #default="{ row }">
                {{ genderText(row.gender) }}
              </template>
            </el-table-column>
            <el-table-column prop="student_no" label="学号" min-width="180" />
            <el-table-column label="所属班级" min-width="180">
              <template #default="{ row }">
                {{ row.class_name || '未分配班级' }}
              </template>
            </el-table-column>
          </template>

          <template v-else>
            <el-table-column prop="student_name" label="学生姓名" min-width="160" />
            <el-table-column prop="student_no" label="学号" width="160" />
            <el-table-column prop="class_name" label="所属班级" width="180" />
            <el-table-column label="选课方式" width="120">
              <template #default="{ row }">
                <el-tag :type="row.can_remove ? 'warning' : 'success'">
                  {{ row.can_remove ? '可移除' : '固定成员' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              v-if="canManageRoster"
              label="操作"
              width="140"
            >
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  :disabled="!row.can_remove"
                  @click="removeStudent(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </template>
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import api from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const students = ref([])

const selectedCourse = computed(() => userStore.selectedCourse)
const isAdminView = computed(() => userStore.isAdmin)
const canManageRoster = computed(() => userStore.canManageTeaching && !isAdminView.value)
const showCourseEmpty = computed(() => !isAdminView.value && !selectedCourse.value)

const pageSubtitle = computed(() => {
  if (isAdminView.value) {
    return '查看全部学生的姓名、性别、学号和所属班级。'
  }

  if (selectedCourse.value) {
    return `${selectedCourse.value.name} · ${selectedCourse.value.class_name || '未分配班级'}`
  }

  return '请先选择一门课程查看课程学生名单。'
})

const genderText = gender => {
  if (gender === 'male') {
    return '男'
  }
  if (gender === 'female') {
    return '女'
  }
  return '-'
}

const loadAllStudents = async () => {
  const allStudents = []
  const pageSize = 1000
  let page = 1
  let total = 0

  do {
    const result = await api.students.list({ page, page_size: pageSize })
    const pageData = result?.data || []
    total = result?.total || pageData.length
    allStudents.push(...pageData)

    if (pageData.length < pageSize) {
      break
    }

    page += 1
  } while (allStudents.length < total)

  return allStudents
}

const loadStudents = async () => {
  loading.value = true

  try {
    if (isAdminView.value) {
      students.value = await loadAllStudents()
      return
    }

    if (!selectedCourse.value) {
      students.value = []
      return
    }

    students.value = await api.courses.getStudents(selectedCourse.value.id)
  } catch (error) {
    console.error('加载学生数据失败', error)
    ElMessage.error('加载学生数据失败')
  } finally {
    loading.value = false
  }
}

const removeStudent = async row => {
  try {
    await ElMessageBox.confirm(
      `确认将 ${row.student_name} 从 ${selectedCourse.value.name} 中移除吗？`,
      '移除学生',
      { type: 'warning' }
    )
    await api.courses.removeStudent(selectedCourse.value.id, row.student_id)
    ElMessage.success('学生已从课程中移除')
    await loadStudents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除学生失败', error)
    }
  }
}

onMounted(() => {
  loadStudents()
})

watch([selectedCourse, isAdminView], () => {
  loadStudents()
})
</script>

<style scoped>
.students-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px;
  font-size: 28px;
  color: #0f172a;
}

.page-subtitle {
  margin: 0;
  color: #64748b;
}

.info-alert {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-count {
  margin-left: 12px;
  color: #64748b;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }
}
</style>
