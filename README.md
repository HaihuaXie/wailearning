# 班级管理系统 (DD-CLASS)

一个现代化的班级管理系统，使用 FastAPI 后端和 Vue3 前端构建，支持学生管理、成绩管理、考勤管理等核心功能。

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-42b883.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791.svg)
![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)

## � 系统预览

### Dashboard 数据仪表盘
![Dashboard 数据仪表盘](https://picui.ogmua.cn/s1/2026/03/24/69c2a7b335034.webp)

### Dashboard 数据仪表盘
![Dashboard](https://picui.ogmua.cn/s1/2026/03/24/69c2a7b38b934.webp)

### 学生管理
![学生管理](https://picui.ogmua.cn/s1/2026/03/24/69c2a7b3b291e.webp)

### 成绩管理
![成绩管理](https://picui.ogmua.cn/s1/2026/03/24/69c2a7b3cc451.webp)

### 考勤管理
![考勤管理](https://picui.ogmua.cn/s1/2026/03/24/69c2a7b42417f.webp)

### 班级排名
![班级排名](https://picui.ogmua.cn/s1/2026/03/24/69c2a7bf4c3d6.webp)

### 数据分析
![数据分析](https://picui.ogmua.cn/s1/2026/03/24/69c2a7bf814cf.webp)

### 用户管理
![用户管理](https://picui.ogmua.cn/s1/2026/03/24/69c2a7bf98a28.webp)

---

## �📋 目录

- [功能介绍](#功能介绍)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [API文档](#api文档)
- [数据库迁移](#数据库迁移)
- [常见问题](#常见问题)
- [使用许可](#使用许可)

## 🎯 功能介绍

### 1. 用户认证与权限管理
- ✅ 用户注册与登录（JWT Token认证）
- ✅ 角色权限管理（管理员/教师）
- ✅ 班级访问权限控制

### 2. 班级管理
- ✅ 创建、编辑、删除班级
- ✅ 班级信息维护（名称、年级）
- ✅ 班级学生数量统计

### 3. 学生管理
- ✅ 学生档案管理（基本信息、联系方式）
- ✅ 学号管理（支持班级内唯一）
- ✅ 批量导入学生（支持Excel/CSV格式）
- ✅ 按班级筛选和搜索

### 4. 成绩管理
- ✅ 成绩录入与修改
- ✅ 多种考试类型支持（期中、期末、测验等）
- ✅ 按学期、班级、学生筛选成绩
- ✅ 批量导入成绩（支持Excel格式）
- ✅ 成绩统计与分析

### 5. 考勤管理
- ✅ 日常考勤记录（出勤、缺勤、迟到、请假）
- ✅ 日历视图展示考勤状态
- ✅ 批量设置全班考勤
- ✅ Excel批量导入考勤数据
- ✅ 考勤统计与出勤率计算

### 6. 学期管理
- ✅ 学期创建与管理
- ✅ 数据按学期筛选
- ✅ 预设默认学期（2024-1至2025-2）

### 7. 数据可视化
- ✅ Dashboard统计概览
- ✅ 班级平均成绩排名
- ✅ 学生成绩趋势分析
- ✅ 考勤率统计

## 🛠 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+
- **ORM**: SQLAlchemy
- **认证**: JWT (PyJWT)
- **验证**: Pydantic

### 前端
- **框架**: Vue.js 3.4+
- **构建工具**: Vite 5.0+
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4.0+
- **图表**: ECharts 5.0+
- **Excel处理**: xlsx

### 开发工具
- **代码格式化**: Prettier
- **版本控制**: Git

## 🚀 快速开始

### 前置要求

- Python 3.9 或更高版本
- Node.js 18 或更高版本
- PostgreSQL 14 或更高版本
- npm 或 yarn 包管理器

### 1. 克隆项目

```bash
git clone https://github.com/joyapple/DD-CLASS.git
cd DD-CLASS
```

### 2. 启动后端

```bash
# 进入后端目录
cd app

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后，访问 http://localhost:8000/docs 查看API文档

### 3. 启动前端

```bash
# 新开一个终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后，访问 http://localhost:3000

### 4. 默认登录账户

```
用户名: admin
密码: admin123
```

⚠️ **重要**: 请在生产环境中修改默认密码！

## 📦 安装指南

### 后端安装

#### 1. 安装Python依赖

```bash
cd app
pip install -r requirements.txt
```

#### 2. 配置数据库

确保PostgreSQL服务已启动，并创建数据库：

```sql
CREATE DATABASE ddclass;
CREATE USER ddclass_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ddclass TO ddclass_user;
```

#### 3. 修改配置文件

编辑 `app/config.py` 或创建 `.env` 文件：

```env
DATABASE_URL=postgresql://ddclass_user:your_password@localhost:5432/ddclass
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 前端安装

```bash
cd frontend
npm install
```

如果安装缓慢，可以使用淘宝镜像：

```bash
npm install --registry=https://registry.npmmirror.com
```

## ⚙️ 配置说明

### 后端配置

#### 数据库配置 (app/config.py)

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@host:5432/dbname"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
```

#### 环境变量

支持以下环境变量（优先级从高到低）：

1. `.env` 文件
2. 系统环境变量
3. 默认值

### 前端配置

#### API代理配置 (vite.config.js)

如果后端不在本地运行，修改代理目标：

```javascript
proxy: {
  '/api': {
    target: 'http://your-backend-server:8000',
    changeOrigin: true
  }
}
```

#### 开发环境端口

默认前端运行在 3000 端口，后端运行在 8000 端口。

## 📖 使用指南

### 首次使用

1. **启动服务**: 按照快速开始指南启动前后端服务
2. **登录系统**: 使用默认账户登录
3. **初始化数据**: 
   - 如果数据库为空，系统会自动初始化默认学期
   - 可以手动添加班级、学生等数据

### 日常使用流程

#### 1. 学生管理
- 创建班级
- 添加学生（或批量导入）
- 管理学生信息

#### 2. 成绩管理
- 选择班级和学期
- 录入学生成绩
- 查看成绩统计

#### 3. 考勤管理
- 使用日历视图快速查看考勤状态
- 批量设置全班考勤
- 导入历史考勤数据

#### 4. 数据分析
- 查看Dashboard统计
- 分析成绩趋势
- 监控考勤率

### 批量导入说明

#### Excel模板格式

**学生导入** (`students_import.xlsx`):
```csv
姓名,学号,性别,电话,家长电话,地址,班级ID
张三,001,男,13800138000,13900139000,北京市,1
```

**成绩导入** (`scores_import.xlsx`):
```csv
学号,班级ID,科目ID,分数,考试类型,考试日期,学期
001,1,1,95,期中,2024-03-20,2024-1
```

**考勤导入** (`attendance_import.xlsx`):
```csv
学号,日期,状态,备注
001,2024-03-20,出勤,
002,2024-03-20,缺勤,病假
```

#### 导入步骤

1. 下载对应模板
2. 填写数据（注意编码，建议使用UTF-8）
3. 上传文件
4. 系统自动验证并导入
5. 查看导入结果

## 📁 项目结构

```
DD-CLASS/
├── app/                          # 后端应用
│   ├── routers/                  # API路由
│   │   ├── auth.py              # 认证相关API
│   │   ├── classes.py           # 班级管理API
│   │   ├── students.py          # 学生管理API
│   │   ├── scores.py            # 成绩管理API
│   │   ├── attendance.py        # 考勤管理API
│   │   ├── semesters.py         # 学期管理API
│   │   ├── subjects.py          # 科目管理API
│   │   ├── dashboard.py         # 仪表盘API
│   │   └── users.py             # 用户管理API
│   ├── models.py                # 数据库模型
│   ├── schemas.py               # Pydantic模型
│   ├── auth.py                  # 认证逻辑
│   ├── config.py                # 配置文件
│   ├── database.py              # 数据库连接
│   └── main.py                  # 应用入口
├── frontend/                     # 前端应用
│   ├── src/
│   │   ├── api/                # API客户端
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia状态管理
│   │   ├── views/              # 页面组件
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口文件
│   ├── package.json             # 前端依赖
│   └── vite.config.js          # Vite配置
├── .gitignore                   # Git忽略文件
├── requirements.txt             # Python依赖
└── README.md                    # 项目说明文档
```

## 📚 API文档

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

| 模块 | 方法 | 端点 | 描述 |
|------|------|------|------|
| 认证 | POST | /api/auth/login | 用户登录 |
| 认证 | POST | /api/auth/register | 用户注册 |
| 班级 | GET | /api/classes | 获取班级列表 |
| 班级 | POST | /api/classes | 创建班级 |
| 学生 | GET | /api/students | 获取学生列表 |
| 学生 | POST | /api/students/batch | 批量导入学生 |
| 成绩 | GET | /api/scores | 获取成绩列表 |
| 成绩 | POST | /api/scores/batch | 批量导入成绩 |
| 考勤 | GET | /api/attendance | 获取考勤列表 |
| 考勤 | POST | /api/attendance/batch | 批量导入考勤 |
| 考勤 | POST | /api/attendance/class-batch | 班级批量考勤 |
| 学期 | GET | /api/semesters | 获取学期列表 |
| 学期 | POST | /api/semesters | 创建学期 |
| 统计 | GET | /api/dashboard/stats | 获取统计数据 |

## 🗄 数据库迁移

### 首次初始化

如果数据库为空，运行初始化脚本：

```bash
cd app
python init_db.py
```

### 执行数据库迁移

当模型更新时，运行迁移脚本：

```bash
python migrate_v2.py
```

### 迁移脚本说明

- `init_db.py`: 创建默认管理员账户和基础数据
- `migrate_v2.py`: 数据库结构迁移（学期表、约束更新等）

## ❓ 常见问题

### 1. 数据库连接失败

**问题**: `could not connect to server`

**解决**: 
- 确认PostgreSQL服务已启动
- 检查DATABASE_URL配置
- 验证用户名密码正确

### 2. 前端代理请求失败

**问题**: `502 Bad Gateway` 或 `404 Not Found`

**解决**:
- 确认后端服务正在运行
- 检查vite.config.js中的代理配置
- 确保端口号正确

### 3. 导入文件乱码

**问题**: 导入Excel后显示乱码

**解决**:
- 使用UTF-8编码保存文件
- 或使用xlsx格式（自动处理编码）
- Excel保存时选择"CSV UTF-8"格式

### 4. 端口被占用

**问题**: `Port is already in use`

**解决**:
```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程
taskkill /PID <进程ID> /F

# 或使用其他端口启动
python -m uvicorn app.main:app --port 8001
```

### 5. 依赖安装失败

**问题**: `pip install` 报错

**解决**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📄 使用许可

### 开源许可

本项目基于 **Apache License 2.0** 开源许可。

### 许可条款

Apache License 2.0

Copyright 2024 DD-CLASS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

### 第三方组件许可

本项目使用的开源组件：

- **FastAPI**: MIT License
- **Vue.js**: MIT License
- **Element Plus**: MIT License
- **SQLAlchemy**: MIT License
- **PostgreSQL**: PostgreSQL License
- **ECharts**: Apache-2.0 License

### 注意事项

1. 本项目仅供学习和教育目的使用
2. 允许自由使用、修改和分发
3. 商业使用请注明原作者和出处
4. 作者不对使用本项目造成的任何损失负责

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue

- 描述清楚问题或建议
- 提供复现步骤（如适用）
- 说明环境信息（操作系统、Python版本等）

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

- **GitHub Issues**: https://github.com/joyapple/DD-CLASS/issues
- **作者**: joyapple

## 🙏 致谢

感谢以下开源项目的贡献：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [ECharts](https://echarts.apache.org/)

---

<div align="center">

Made with ❤️ by [joyapple](https://github.com/joyapple)

</div>
