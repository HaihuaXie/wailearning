<template>
  <el-container class="layout-container">
    <el-aside 
      :width="isCollapsed ? '64px' : '220px'"
      class="sidebar"
      :class="{ 'sidebar-collapsed': isCollapsed }"
    >
      <div class="logo" :class="{ 'logo-collapsed': isCollapsed }">
        <div class="logo-content">
          <el-icon class="logo-icon" :size="24"><School /></el-icon>
          <transition name="fade-slide">
            <h2 v-if="!isCollapsed" class="logo-text">班级管理</h2>
          </transition>
        </div>
        <el-button
          class="collapse-btn"
          :icon="isCollapsed ? Expand : Fold"
          @click="toggleCollapse"
          circle
          size="small"
          :type="isCollapsed ? 'primary' : 'info'"
        />
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="true"
        router
        class="sidebar-menu"
        :class="{ 'menu-collapsed': isCollapsed }"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/classes" v-if="userStore.isAdmin">
          <el-icon><School /></el-icon>
          <template #title>班级管理</template>
        </el-menu-item>
        <el-menu-item index="/students">
          <el-icon><User /></el-icon>
          <template #title>学生管理</template>
        </el-menu-item>
        <el-menu-item index="/scores">
          <el-icon><Document /></el-icon>
          <template #title>成绩管理</template>
        </el-menu-item>
        <el-menu-item index="/attendance">
          <el-icon><Calendar /></el-icon>
          <template #title>考勤管理</template>
        </el-menu-item>
        <el-menu-item index="/rankings">
          <el-icon><TrendCharts /></el-icon>
          <template #title>班级排名</template>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><PieChart /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        <el-menu-item index="/users" v-if="userStore.isAdmin">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/subjects" v-if="userStore.isAdmin">
          <el-icon><Reading /></el-icon>
          <template #title>科目管理</template>
        </el-menu-item>
        <el-menu-item index="/semesters" v-if="userStore.isAdmin">
          <el-icon><Collection /></el-icon>
          <template #title>学期管理</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-if="!isCollapsed">
        <el-text class="version-text">v1.0.0</el-text>
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar">
                {{ userStore.userInfo?.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.real_name }}</span>
              <el-tag :type="getRoleTagType(userStore.userInfo?.role)" size="small" effect="dark">
                {{ getRoleText(userStore.userInfo?.role) }}
              </el-tag>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>

      <el-footer class="footer">
        <div class="footer-content">
          <el-text class="footer-text">
            © 2024 DD-CLASS 班级管理系统 | Made with ❤️
          </el-text>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis,
  School,
  User,
  Document,
  Calendar,
  TrendCharts,
  PieChart,
  UserFilled,
  Reading,
  SwitchButton,
  Collection,
  Expand,
  Fold,
  Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const currentRouteName = computed(() => {
  const routeMap = {
    '/dashboard': '数据仪表盘',
    '/classes': '班级管理',
    '/students': '学生管理',
    '/scores': '成绩管理',
    '/attendance': '考勤管理',
    '/rankings': '班级排名',
    '/analysis': '数据分析',
    '/users': '用户管理',
    '/subjects': '科目管理',
    '/semesters': '学期管理'
  }
  return routeMap[route.path] || '页面'
})

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const getRoleText = (role) => {
  const roleMap = {
    'admin': '管理员',
    'class_teacher': '班主任',
    'teacher': '任课教师'
  }
  return roleMap[role] || '未知角色'
}

const getRoleTagType = (role) => {
  const typeMap = {
    'admin': 'danger',
    'class_teacher': 'warning',
    'teacher': 'success'
  }
  return typeMap[role] || 'info'
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  transition: width 0.3s ease;
  position: relative;
  overflow-x: hidden;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-collapsed {
  width: 64px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: rgba(0, 0, 0, 0.15);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-collapsed {
  justify-content: center;
  padding: 0 8px;
}

.logo-content {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.logo-icon {
  color: #409eff;
  flex-shrink: 0;
}

.logo-text {
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  letter-spacing: 1px;
}

.collapse-btn {
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  transform: scale(1.1);
}

.sidebar-menu {
  border-right: none;
  background: transparent !important;
  margin-top: 10px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.sidebar-menu .el-menu-item {
  height: 56px;
  line-height: 56px;
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: 500;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item:hover .el-icon {
  color: white !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, #409eff 0%, #66b1ff 100%) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  font-weight: 600;
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  color: white !important;
}

.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: white;
  border-radius: 0 4px 4px 0;
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.15);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.version-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.header {
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: #f5f7fa;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.username {
  font-weight: 500;
  color: #303133;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  min-height: calc(100vh - 124px);
}

.footer {
  background: white;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #ebeef5;
}

.footer-content {
  text-align: center;
}

.footer-text {
  color: #909399;
  font-size: 13px;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

:deep(.el-menu--collapse .el-menu-item .el-icon) {
  margin: 0;
}

:deep(.el-menu--collapse .el-menu-item) {
  padding: 0 20px !important;
  justify-content: center;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
