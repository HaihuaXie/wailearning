<template>
  <div class="students-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">学生管理</h1>
        <p class="page-subtitle">
          {{ selectedCourse ? `${selectedCourse.name} · ${selectedCourse.class_name || '未分配班级'}` : '请先选择一门课程查看课程学生名单。' }}
        </p>
      </div>
      <el-button @click="router.push('/courses')">切换课程</el-button>
    </div>

    <el-empty
      v-if="!selectedCourse"
      description="请先从“我的课程”中选择一门课程。"
    />

    <template v-else>
      <el-alert
        :title="selectedCourse.course_type === 'elective' ? '当前为选修课，可移除学生。' : '当前为必修课，系统已自动加入班级全部学生，且不可移除。'"
        :type="selectedCourse.course_type === 'elective' ? 'warning' : 'info'"
        :closable="false"
        class="info-alert"
      />

      <el-card shadow="never">
        <template #header>
          <div class="card-header">
            <div>
              <strong>课程学生名单</strong>
              <span class="header-count">共 {{ students.length }} 人</span>
            </div>
          </div>
        </template>

        <el-table :data="students" v-loading="loading">
          <el-table-column prop="student_name" label="学生姓名" min-width="160" />
          <el-table-column prop="student_no" label="学号" width="160" />
          <el-table-column prop="class_name" label="所属班级" width="180" />
          <el-table-column label="选课方式" width="120">
            <template #default="{ row }">
              <el-tag :type="row.can_remove ? 'warning' : 'success'">
                {{ row.can_remove ? '可退选' : '固定成员' }}
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
const canManageRoster = computed(() => userStore.canManageTeaching)

const loadStudents = async () => {
  if (!selectedCourse.value) {
    students.value = []
    return
  }

  loading.value = true
  try {
    students.value = await api.courses.getStudents(selectedCourse.value.id)
  } catch (error) {
    console.error('加载课程学生失败', error)
    ElMessage.error('加载课程学生失败')
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

watch(selectedCourse, () => {
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
