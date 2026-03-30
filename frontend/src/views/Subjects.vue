<template>
  <div class="courses-admin-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">课程管理</h1>
        <p class="page-subtitle">创建课程时可指定课程类型、班级和任课老师，系统会自动同步班级学生到课程名单。</p>
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
        <el-table-column prop="student_count" label="学生数" width="100" />
        <el-table-column prop="description" label="课程简介" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="200">
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
      width="620px"
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
        <el-form-item label="所属学期" prop="semester">
          <el-select v-model="form.semester" placeholder="请选择学期" style="width: 100%" clearable>
            <el-option v-for="item in semesters" :key="item.id" :label="item.name" :value="item.name" />
          </el-select>
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
  course_type: 'required',
  status: 'active',
  semester: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择所属班级', trigger: 'change' }],
  course_type: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择课程状态', trigger: 'change' }]
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    class_id: null,
    teacher_id: null,
    course_type: 'required',
    status: 'active',
    semester: '',
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

const openCreateDialog = () => {
  editingCourse.value = null
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = course => {
  editingCourse.value = course
  Object.assign(form, {
    name: course.name,
    class_id: course.class_id,
    teacher_id: course.teacher_id,
    course_type: course.course_type || 'required',
    status: course.status || 'active',
    semester: course.semester || '',
    description: course.description || ''
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingCourse.value) {
      await api.courses.update(editingCourse.value.id, { ...form })
      ElMessage.success('课程已更新')
    } else {
      await api.courses.create({ ...form })
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

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }
}
</style>
