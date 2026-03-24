<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="system-name">班级管理系统</h1>
        <p class="system-desc">DD-CLASS 管理平台</p>
      </div>

      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名 / Username"
            :prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码 / Password"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary"
            size="large"
            :loading="loading" 
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tips">
        <el-icon><InfoFilled /></el-icon>
        <span>默认账号：admin / admin123</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form.username, form.password)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        console.error(error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to bottom right, #ffffff 0%, #f8fafc 100%);
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(to bottom, #3b82f6 0%, #1e40af 100%);
}

.login-card {
  position: relative;
  width: 420px;
  padding: 48px 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
              0 2px 4px -1px rgba(0, 0, 0, 0.06),
              0 0 0 1px rgba(0, 0, 0, 0.05);
  margin: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.system-name {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.system-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  letter-spacing: 1px;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: #cbd5e1;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.login-form :deep(.el-input__inner) {
  font-size: 15px;
  height: 24px;
  line-height: 24px;
}

.login-form :deep(.el-input__prefix .el-icon) {
  font-size: 18px;
  color: #94a3b8;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  background: #1e40af;
  border: none;
  border-radius: 6px;
  transition: background 0.2s;
}

.login-btn:hover {
  background: #1e3a8a;
}

.login-btn:active {
  background: #1e3a8a;
  transform: translateY(1px);
}

.login-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 6px;
  color: #64748b;
  font-size: 13px;
}

.login-tips .el-icon {
  color: #3b82f6;
  font-size: 16px;
}

@media (max-width: 480px) {
  .login-card {
    width: calc(100% - 40px);
    padding: 32px 24px;
  }

  .system-name {
    font-size: 24px;
  }

  .login-form :deep(.el-form-item) {
    margin-bottom: 20px;
  }
}
</style>
