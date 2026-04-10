<template>
  <div class="courses-admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">课程管理</h1>
        <p class="page-subtitle">管理员可以统一查看、编辑课程信息与课程时间安排。</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        新建课程
      </el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="courses" v-loading="loading">
        <el-table-column prop="name" label="课程名称" min-width="180" />
        <el-table-column prop="class_name" label="班级" width="160" />
        <el-table-column prop="teacher_name" label="任课老师" width="160" />
        <el-table-column label="课程类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.course_type === 'elective' ? 'warning' : 'success'">
              {{ row.course_type === 'elective' ? '选修课' : '必修课' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'info' : 'primary'">
              {{ row.status === 'completed' ? '已结束' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="学期" width="140" />
        <el-table-column label="课程时间" min-width="360">
          <template #default="{ row }">
            <div v-if="getCourseTimeLines(row).length" class="course-time-list">
              <div
                v-for="(line, index) in getCourseTimeLines(row)"
                :key="`${row.id}-${index}`"
                class="course-time-line"
              >
                {{ line }}
              </div>
            </div>
            <span v-else>未设置</span>
          </template>
        </el-table-column>
        <el-table-column prop="student_count" label="学生数" width="100" />
        <el-table-column prop="description" label="课程简介" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteCourse(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingCourse ? '编辑课程' : '新建课程'"
      width="960px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="所属班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" style="width: 100%">
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任课老师" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="请选择任课老师" style="width: 100%" clearable>
            <el-option v-for="item in teachers" :key="item.id" :label="item.real_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type">
          <el-radio-group v-model="form.course_type">
            <el-radio label="required">必修课</el-radio>
            <el-radio label="elective">选修课</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="课程状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="active">进行中</el-radio>
            <el-radio label="completed">已结束</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="所属学期" prop="semester_id">
          <el-select v-model="form.semester_id" placeholder="请选择学期" style="width: 100%" clearable>
            <el-option v-for="item in semesters" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="课程时间" prop="course_times" class="course-times-form-item">
          <div class="course-times-editor">
            <div
              v-for="(courseTime, index) in form.course_times"
              :key="`course-time-${index}`"
              class="course-time-panel"
            >
              <div class="course-time-panel__header">
                <div>
                  <div class="course-time-panel__title">课程时间 {{ index + 1 }}</div>
                  <div class="course-time-panel__subtitle">
                    设置这一段时间内的起始日期、结束日期和每周时间
                  </div>
                </div>
                <el-button
                  v-if="form.course_times.length > 1"
                  text
                  type="danger"
                  @click="removeCourseTime(index)"
                >
                  删除
                </el-button>
              </div>

              <div class="course-time-panel__fields">
                <el-form-item :prop="`course_times.${index}.course_start_at`" label="起始日期" label-width="80px">
                  <el-date-picker
                    v-model="courseTime.course_start_at"
                    type="date"
                    placeholder="请选择起始日期"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>

                <el-form-item :prop="`course_times.${index}.course_end_at`" label="结束日期" label-width="80px">
                  <el-date-picker
                    v-model="courseTime.course_end_at"
                    type="date"
                    placeholder="请选择结束日期"
                    style="width: 100%"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
              </div>

              <div class="course-time-panel__schedule">
                <div class="course-time-panel__schedule-label">每周时间</div>
                <CourseSchedulePicker v-model="courseTime.weekly_schedule" />
              </div>
            </div>

            <el-button plain class="course-times-editor__add" @click="addCourseTime">
              添加课程时间
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="课程简介" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import api from '@/api'
import CourseSchedulePicker from '@/components/CourseSchedulePicker.vue'
import { parseScheduleValue } from '@/utils/courseSchedule'
import {
  createEmptyCourseTime,
  formatCourseTimeEntry,
  normalizeEditableCourseTimes,
  serializeCourseTimesPayload
} from '@/utils/courseTimes'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingCourse = ref(null)
const formRef = ref(null)

const courses = ref([])
const classes = ref([])
const teachers = ref([])
const semesters = ref([])

const form = reactive({
  name: '',
  class_id: null,
  teacher_id: null,
  semester_id: null,
  course_type: 'required',
  status: 'active',
  course_times: [createEmptyCourseTime()],
  description: ''
})

const validateCourseTimes = (_rule, value, callback) => {
  if (!Array.isArray(value) || !value.length) {
    callback(new Error('请至少添加一组课程时间'))
    return
  }

  for (const item of value) {
    if (!item.course_start_at || !item.course_end_at) {
      callback(new Error('请为每组课程时间选择起始日期和结束日期'))
      return
    }

    if (new Date(item.course_end_at) < new Date(item.course_start_at)) {
      callback(new Error('课程时间的结束日期不能早于起始日期'))
      return
    }

    if (!parseScheduleValue(item.weekly_schedule).length) {
      callback(new Error('请为每组课程时间选择每周时间'))
      return
    }
  }

  callback()
}

const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择所属班级', trigger: 'change' }],
  course_type: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择课程状态', trigger: 'change' }],
  course_times: [{ validator: validateCourseTimes, trigger: 'change' }]
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    class_id: null,
    teacher_id: null,
    semester_id: null,
    course_type: 'required',
    status: 'active',
    course_times: [createEmptyCourseTime()],
    description: ''
  })
}

const loadCourses = async () => {
  loading.value = true
  try {
    courses.value = await api.courses.list()
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  const [classData, userData, semesterData] = await Promise.all([
    api.classes.list(),
    api.users.list(),
    api.semesters.list()
  ])
  classes.value = classData || []
  teachers.value = (userData || []).filter(item => ['teacher', 'class_teacher'].includes(item.role))
  semesters.value = semesterData || []
}

const addCourseTime = () => {
  form.course_times.push(createEmptyCourseTime())
  formRef.value?.clearValidate('course_times')
}

const removeCourseTime = index => {
  if (form.course_times.length <= 1) {
    return
  }

  form.course_times.splice(index, 1)
  formRef.value?.clearValidate('course_times')
}

const openCreateDialog = () => {
  editingCourse.value = null
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = course => {
  editingCourse.value = course
  const normalizedCourseTimes = normalizeEditableCourseTimes(course)

  Object.assign(form, {
    name: course.name,
    class_id: course.class_id,
    teacher_id: course.teacher_id,
    semester_id: course.semester_id ?? null,
    course_type: course.course_type || 'required',
    status: course.status || 'active',
    course_times: normalizedCourseTimes.length ? normalizedCourseTimes : [createEmptyCourseTime()],
    description: course.description || ''
  })
  dialogVisible.value = true
}

const getCourseTimeLines = course =>
  normalizeEditableCourseTimes(course)
    .map(formatCourseTimeEntry)
    .filter(Boolean)

const submitForm = async () => {
  await formRef.value.validate()
  submitting.value = true

  try {
    const payload = {
      name: form.name,
      class_id: form.class_id,
      teacher_id: form.teacher_id,
      semester_id: form.semester_id || null,
      course_type: form.course_type,
      status: form.status,
      course_times: serializeCourseTimesPayload(form.course_times),
      description: form.description
    }

    if (editingCourse.value) {
      await api.courses.update(editingCourse.value.id, payload)
      ElMessage.success('课程已更新')
    } else {
      await api.courses.create(payload)
      ElMessage.success('课程已创建')
    }

    dialogVisible.value = false
    await loadCourses()
  } finally {
    submitting.value = false
  }
}

const deleteCourse = async course => {
  try {
    await ElMessageBox.confirm(`确认删除课程“${course.name}”吗？`, '删除课程', { type: 'warning' })
    await api.courses.delete(course.id)
    ElMessage.success('课程已删除')
    await loadCourses()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除课程失败', error)
    }
  }
}

onMounted(async () => {
  await Promise.all([loadCourses(), loadOptions()])
})
</script>

<style scoped>
.courses-admin-page {
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

.course-time-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-time-line {
  line-height: 1.6;
  color: #334155;
}

.course-times-editor {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-times-editor__add {
  align-self: flex-start;
}

.course-time-panel {
  border: 1px solid #dbe4f0;
  border-radius: 18px;
  padding: 18px;
  background: #f8fbff;
}

.course-time-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.course-time-panel__title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.course-time-panel__subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #64748b;
}

.course-time-panel__fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.course-time-panel__fields :deep(.el-form-item) {
  margin-bottom: 0;
}

.course-time-panel__schedule {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.course-time-panel__schedule-label {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .course-time-panel__fields {
    grid-template-columns: 1fr;
  }

  .course-time-panel__header {
    flex-direction: column;
  }
}
</style>
