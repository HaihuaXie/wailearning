<template>
  <div class="students">
    <div class="page-header">
      <h1 class="page-title">学生管理</h1>
      <div>
        <el-select v-model="filterClassId" placeholder="选择班级" clearable style="width: 180px; margin-right: 10px;">
          <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="searchName" placeholder="搜索学生姓名" style="width: 180px; margin-right: 10px;" clearable @change="loadStudents" />
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增学生
        </el-button>
        <el-button type="success" @click="showBatchDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="students" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_no" label="学号" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column prop="parent_phone" label="家长电话" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadStudents"
        @current-change="loadStudents"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="form.student_no" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="选择班级" style="width: 100%;">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="家长电话" prop="parent_phone">
          <el-input v-model="form.parent_phone" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBatchDialog" title="批量导入学生" width="800px">
      <div style="margin-bottom: 15px;">
        <el-alert title="导入说明" type="info" :closable="false">
          <ol style="margin: 10px 0 0 20px; padding: 0;">
            <li>请先<strong>下载模板</strong>获取Excel文件（推荐使用.xlsx格式）</li>
            <li>按照模板格式填写学生信息</li>
            <li>性别填写"男"或"女"，学号全局唯一不能重复</li>
            <li>选择班级后，上传Excel或CSV文件并点击"导入"</li>
          </ol>
        </el-alert>
        <el-alert type="success" style="margin-top: 10px;">
          <strong>推荐：</strong>使用.xlsx格式的Excel文件，无需担心编码问题！
        </el-alert>
      </div>
      <el-form :model="batchForm" label-width="80px">
        <el-form-item label="选择班级">
          <el-select v-model="batchForm.class_id" placeholder="选择班级" style="width: 100%;">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            accept=".csv,.xlsx"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击选择文件</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持CSV和Excel文件（.csv, .xlsx）</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item v-if="batchForm.studentData">
          <el-input
            v-model="batchForm.studentData"
            type="textarea"
            :rows="10"
            placeholder="预览数据"
            readonly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="downloadTemplate">下载模板</el-button>
        <el-button @click="showBatchDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchImport" :loading="batchLoading">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

const baseURL = '/api'

const students = ref([])
const classes = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const showBatchDialog = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const batchLoading = ref(false)
const uploadRef = ref(null)

const searchName = ref('')
const filterClassId = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  name: '',
  student_no: '',
  gender: 'male',
  class_id: null,
  phone: '',
  parent_phone: '',
  address: ''
})

const batchForm = reactive({
  class_id: null,
  studentData: '',
  studentList: []
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }]
}

const getAuthHeader = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const loadClasses = async () => {
  const res = await axios.get(`${baseURL}/classes`, { headers: getAuthHeader() })
  classes.value = (res.data || []).filter(c => c.id)
}

const loadStudents = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${baseURL}/students`, {
      params: {
        class_id: filterClassId.value,
        name: searchName.value,
        page: page.value,
        page_size: pageSize.value
      },
      headers: getAuthHeader()
    })
    students.value = res.data?.data || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, {
    name: '',
    student_no: '',
    gender: 'male',
    class_id: classes.value[0]?.id || null,
    phone: '',
    parent_phone: '',
    address: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, {
    name: row.name,
    student_no: row.student_no,
    gender: row.gender,
    class_id: row.class_id,
    phone: row.phone,
    parent_phone: row.parent_phone,
    address: row.address
  })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该学生吗?', '提示', { type: 'warning' })
    await axios.delete(`${baseURL}/students/${row.id}`, { headers: getAuthHeader() })
    ElMessage.success('删除成功')
    loadStudents()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  try {
    if (isEdit.value) {
      await axios.put(`${baseURL}/students/${editingId.value}`, form, { headers: getAuthHeader() })
      ElMessage.success('修改成功')
    } else {
      await axios.post(`${baseURL}/students`, form, { headers: getAuthHeader() })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadStudents()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const downloadTemplate = () => {
  const data = [
    ['姓名', '学号', '性别', '电话', '家长电话', '地址'],
    ['张三', '001', '男', '13800138000', '13900139000', '北京市'],
    ['李四', '002', '女', '13800138001', '13900139001', '上海市'],
    ['王五', '003', '男', '13800138002', '13900139002', '广州市']
  ]
  
  const ws = XLSX.utils.aoa_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生信息')
  
  XLSX.writeFile(wb, '学生导入模板.xlsx')
}

const handleFileChange = (uploadFile) => {
  const fileName = uploadFile.name
  const fileExt = fileName.substring(fileName.lastIndexOf('.')).toLowerCase()
  
  if (fileExt === '.xlsx' || fileExt === '.xls') {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
        
        if (jsonData.length > 1) {
          const header = jsonData[0].map(h => String(h).trim())
          const rows = jsonData.slice(1).filter(row => row.some(cell => cell !== undefined && cell !== null && cell !== ''))
          
          batchForm.studentList = rows.map(row => {
            const getValue = (index) => row[index] !== undefined ? String(row[index]).trim() : ''
            
            return {
              name: getValue(header.indexOf('姓名')),
              student_no: getValue(header.indexOf('学号')),
              gender: getValue(header.indexOf('性别')) === '女' ? 'female' : 'male',
              phone: getValue(header.indexOf('电话')),
              parent_phone: getValue(header.indexOf('家长电话')),
              address: getValue(header.indexOf('地址'))
            }
          })
          
          const csvLines = rows.map(row => {
            return header.map((col, i) => {
              const value = row[i] !== undefined ? String(row[i]) : ''
              return value
            }).join(',')
          })
          batchForm.studentData = csvLines.join('\n')
          
          console.log('Excel文件解析成功，学生数量:', batchForm.studentList.length)
          ElMessage.success(`Excel文件解析成功，共${batchForm.studentList.length}条数据`)
        } else {
          ElMessage.warning('Excel文件中没有数据')
        }
      } catch (err) {
        console.error('Excel解析失败:', err)
        ElMessage.error('Excel文件解析失败')
      }
    }
    reader.readAsArrayBuffer(uploadFile.raw)
  } else {
    const reader = new FileReader()
    reader.onload = (e) => {
      const arrayBuffer = e.target.result
      const uint8Array = new Uint8Array(arrayBuffer)
      
      let content = new TextDecoder('utf-8').decode(uint8Array)
      content = content.replace(/^\ufeff/, '')
      
      const chineseChars = (content.match(/[\u4e00-\u9fff]/g) || []).length
      
      if (chineseChars === 0) {
        try {
          const gbkContent = new TextDecoder('gbk').decode(uint8Array)
          const gbkChineseChars = (gbkContent.match(/[\u4e00-\u9fff]/g) || []).length
          if (gbkChineseChars > 0 && !gbkContent.includes('\ufffd')) {
            content = gbkContent
            console.log('检测到GBK编码，已自动转换')
          }
        } catch (err) {
          console.log('编码检测失败，保持UTF-8')
        }
      }
      
      const lines = content.split('\n').filter(line => line.trim())
      if (lines.length > 1) {
        lines.shift()
      }
      
      batchForm.studentData = lines.join('\n')
      batchForm.studentList = []
      
      const linesData = batchForm.studentData.split('\n').filter(line => line.trim())
      for (const line of linesData) {
        const parts = line.split(',').map(p => p.trim())
        if (parts.length < 2) continue
        
        const genderMap = { '男': 'male', '女': 'female' }
        batchForm.studentList.push({
          name: parts[0],
          student_no: parts[1],
          gender: genderMap[parts[2]] || 'male',
          phone: parts[3] || '',
          parent_phone: parts[4] || '',
          address: parts[5] || ''
        })
      }
      
      console.log('CSV内容预览:', batchForm.studentData)
    }
    reader.readAsArrayBuffer(uploadFile.raw)
  }
}

const handleBatchImport = async () => {
  if (!batchForm.class_id) {
    ElMessage.warning('请选择班级')
    return
  }
  
  if (!batchForm.studentList || batchForm.studentList.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  batchLoading.value = true
  
  const studentsList = batchForm.studentList.map(s => ({
    ...s,
    class_id: batchForm.class_id
  }))
  
  if (studentsList.length === 0) {
    ElMessage.warning('没有有效的学生数据')
    batchLoading.value = false
    return
  }
  
  try {
    const token = localStorage.getItem('token')
    console.log('准备导入的学生数据:', JSON.stringify(studentsList, null, 2))
    
    const response = await fetch(`${baseURL}/students/batch`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify({ students: studentsList })
    })
    
    const result = await response.json()
    
    if (result.success > 0) {
      ElMessage.success(`成功导入 ${result.success} 名学生`)
    }
    if (result.failed > 0) {
      ElMessage.warning(`导入失败 ${result.failed} 名学生`)
    }
    if (result.errors && result.errors.length > 0) {
      console.log('导入错误:', result.errors)
      ElMessage.warning(`错误详情: ${result.errors.join(', ')}`)
    }
    
    showBatchDialog.value = false
    batchForm.studentData = ''
    batchForm.studentList = []
    batchForm.class_id = null
    loadStudents()
  } catch (e) {
    ElMessage.error('批量导入失败')
  } finally {
    batchLoading.value = false
  }
}

watch([filterClassId], () => {
  page.value = 1
  loadStudents()
})

onMounted(async () => {
  await loadClasses()
  loadStudents()
})
</script>

<style scoped>
.students {
  padding: 20px;
}
</style>
