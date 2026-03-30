<template>
  <div class="courses-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">我的课程</h1>
        <p class="page-subtitle">
          {{ userStore.isStudent ? '选择一门课程查看作业与通知。' : '选择一门课程进入教学工作台。' }}
        </p>
      </div>
      <el-alert
        v-if="userStore.selectedCourse"
        type="success"
        :closable="false"
        class="current-course-alert"
      >
        当前课程：{{ userStore.selectedCourse.name }}
      </el-alert>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :span="24">
        <section class="course-section">
          <div class="section-header">
            <h2>正在进行</h2>
            <span>{{ activeCourses.length }} 门</span>
          </div>
          <el-empty v-if="!activeCourses.length" description="暂无进行中的课程" />
          <div v-else class="course-grid">
            <article
              v-for="course in activeCourses"
              :key="course.id"
              class="course-card"
              :class="{ 'course-card-selected': userStore.selectedCourse?.id === course.id }"
              @click="selectCourse(course)"
            >
              <div class="course-card-header">
                <h3>{{ course.name }}</h3>
                <div class="course-tags">
                  <el-tag type="primary">{{ course.course_type === 'elective' ? '选修课' : '必修课' }}</el-tag>
                  <el-tag type="success">进行中</el-tag>
                </div>
              </div>
              <div class="course-meta">
                <span>班级：{{ course.class_name || '未分配' }}</span>
                <span>任课老师：{{ course.teacher_name || '未分配' }}</span>
                <span>学期：{{ course.semester || '未设置' }}</span>
                <span>学生数：{{ course.student_count || 0 }}</span>
              </div>
              <p class="course-description">{{ course.description || '暂无课程简介。' }}</p>
              <div class="course-actions">
                <el-button type="primary" @click.stop="selectCourse(course)">
                  进入课程
                </el-button>
              </div>
            </article>
          </div>
        </section>
      </el-col>

      <el-col :span="24">
        <section class="course-section">
          <div class="section-header">
            <h2>已结束课程</h2>
            <span>{{ completedCourses.length }} 门</span>
          </div>
          <el-empty v-if="!completedCourses.length" description="暂无已结束课程" />
          <div v-else class="course-grid">
            <article
              v-for="course in completedCourses"
              :key="course.id"
              class="course-card course-card-muted"
              :class="{ 'course-card-selected': userStore.selectedCourse?.id === course.id }"
              @click="selectCourse(course)"
            >
              <div class="course-card-header">
                <h3>{{ course.name }}</h3>
                <div class="course-tags">
                  <el-tag type="info">{{ course.course_type === 'elective' ? '选修课' : '必修课' }}</el-tag>
                  <el-tag type="info">已结束</el-tag>
                </div>
              </div>
              <div class="course-meta">
                <span>班级：{{ course.class_name || '未分配' }}</span>
                <span>任课老师：{{ course.teacher_name || '未分配' }}</span>
                <span>学期：{{ course.semester || '未设置' }}</span>
              </div>
              <div class="course-actions">
                <el-button @click.stop="selectCourse(course)">
                  查看课程
                </el-button>
              </div>
            </article>
          </div>
        </section>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ElMessage } from 'element-plus'

import api from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const courses = ref([])

const activeCourses = computed(() => courses.value.filter(course => course.status !== 'completed'))
const completedCourses = computed(() => courses.value.filter(course => course.status === 'completed'))

const loadCourses = async () => {
  loading.value = true
  try {
    courses.value = await api.courses.list()
  } catch (error) {
    console.error('加载课程失败', error)
    ElMessage.error('加载课程失败')
  } finally {
    loading.value = false
  }
}

const selectCourse = course => {
  userStore.setSelectedCourse(course)
  if (userStore.isStudent) {
    router.push('/homework')
    return
  }
  router.push('/dashboard')
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.courses-page {
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
  font-weight: 700;
  color: #1f2937;
}

.page-subtitle {
  margin: 0;
  color: #64748b;
}

.current-course-alert {
  width: 320px;
}

.course-section {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #0f172a;
}

.section-header span {
  color: #64748b;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.course-card {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.12);
  border-color: #93c5fd;
}

.course-card-selected {
  border-color: #2563eb;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.15);
}

.course-card-muted {
  background: #f8fafc;
}

.course-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.course-card-header h3 {
  margin: 0;
  font-size: 20px;
  color: #111827;
}

.course-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.course-meta {
  display: grid;
  gap: 6px;
  color: #475569;
  font-size: 14px;
}

.course-description {
  margin: 14px 0 0;
  min-height: 42px;
  color: #64748b;
  line-height: 1.6;
}

.course-actions {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .current-course-alert {
    width: 100%;
  }
}
</style>
