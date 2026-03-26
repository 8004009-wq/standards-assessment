# 标准智能评估系统

基于大模型的标准条款智能拆解与评估系统。

## 功能特性

- **评估模版管理**：上传 PDF/Word 标准文件，大模型智能拆解条款
- **Excel 导入**：支持 Excel 导入条款及业务现状，快速创建评估任务
- **评估任务**：创建评估任务，大模型自动评估条款符合性
- **智能评分**：符合 (1 分)、部分符合 (0.6 分)、不符合 (0 分)、不适用 (不计分)
- **等级评定**：优秀 (85-100)、良好 (75-85)、合格 (60-74)、不合格 (0-59)
- **统计分析**：总体评估情况、等级分布
- **报告生成**：自动生成评估报告

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：Vue3 + Element Plus + Vite
- **大模型**：DashScope Qwen3.5-Plus

## 快速启动

### 1. 配置环境变量

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问系统

浏览器打开：http://localhost:3000

首次使用请注册账号。

## API 接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/templates/upload` - 上传标准并拆解条款
- `GET /api/templates` - 获取模版列表
- `POST /api/tasks` - 创建评估任务
- `POST /api/tasks/excel` - Excel 导入创建评估任务（含条款及业务现状）
- `POST /api/tasks/{id}/assess` - 执行智能评估
- `GET /api/tasks` - 获取任务列表
- `GET /api/stats/overview` - 获取统计概览
- `GET /api/tasks/{id}/report` - 生成评估报告

## 目录结构

```
standard-assessment-system/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── models/       # 数据库模型
│   │   ├── services/     # 业务逻辑 (LLM 服务)
│   │   └── main.py       # FastAPI 入口
│   ├── uploads/          # 上传的标准文件
│   ├── reports/          # 生成的报告
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/        # 页面组件
    │   ├── router/       # 路由配置
    │   └── App.vue
    └── package.json
```
