# 部署指南

## 本地开发部署

### 前置要求

- Python 3.8+
- Node.js 16+ (可选，用于前端开发)

### 快速启动

```bash
# 方式一：一键启动
./start.sh

# 方式二：手动启动
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# 前端（新终端）
cd frontend
python3 -m http.server 8080
```

### 访问地址

- 前端：http://localhost:8080
- 后端 API: http://localhost:8001
- API 文档：http://localhost:8001/docs

---

## GitHub Pages 部署（推荐）

GitHub Pages 可以免费托管静态网站，支持 HTTPS。

### 步骤 1: 启用 GitHub Pages

1. 进入 GitHub 仓库 Settings
2. 选择 Pages 菜单
3. Source 选择 `Deploy from a branch`
4. Branch 选择 `gh-pages`，Folder 选择 `/ (root)`
5. 点击 Save

### 步骤 2: 推送前端到 gh-pages

```bash
# 方法一：使用 git subtree
git subtree push --prefix standards-assessment/frontend origin gh-pages

# 方法二：手动推送
cd standards-assessment/frontend
git init
git add .
git commit -m "Deploy to GitHub Pages"
git branch -M gh-pages
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -f origin gh-pages
```

### 步骤 3: 配置后端

由于 GitHub Pages 只托管静态文件，后端需要单独部署：

**选项 A: 使用公共后端服务**
- 修改 `frontend/index.html` 中的 `API_BASE` 地址
- 将后端部署到任意支持 Python 的平台

**选项 B: 使用 GitHub Actions 自动部署后端**
- 配置 GitHub Actions 工作流
- 自动部署到 Railway、Render 等平台

### 访问地址

```
https://YOUR_USERNAME.github.io/YOUR_REPO/standards-assessment/
```

---

## 生产环境部署

### 后端部署选项

#### 选项 1: Railway

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录并部署
railway login
railway init
railway up
```

#### 选项 2: Render

1. 创建新 Web Service
2. 连接 GitHub 仓库
3. 设置 Build Command: `pip install -r standards-assessment/backend/requirements.txt`
4. 设置 Start Command: `uvicorn standards-assessment.backend.main:app --host 0.0.0.0 --port $PORT`

#### 选项 3: 自有服务器

```bash
# 使用 Gunicorn + Nginx
pip install gunicorn

# 启动
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8001

# Nginx 配置
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 前端部署选项

#### 选项 1: Vercel

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd standards-assessment/frontend
vercel --prod
```

#### 选项 2: Netlify

```bash
# 安装 Netlify CLI
npm i -g netlify-cli

# 部署
cd standards-assessment/frontend
netlify deploy --prod
```

#### 选项 3: Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/standards-assessment/frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 配置说明

### 修改 API 地址

编辑 `frontend/index.html`，找到：

```javascript
const API_BASE = 'http://localhost:8001/api';
```

修改为实际的后端地址：

```javascript
const API_BASE = 'https://your-api-domain.com/api';
```

### 数据库配置

默认使用 SQLite，数据存储在 `data/assessments.db`。

如需使用 PostgreSQL，修改 `backend/models.py`：

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/assessment_db"
```

---

## 安全建议

1. **启用 HTTPS**: 生产环境必须使用 HTTPS
2. **配置 CORS**: 修改 `backend/main.py` 中的 CORS 配置
3. **添加认证**: 实现用户登录和权限控制
4. **数据备份**: 定期备份数据库文件
5. **日志监控**: 配置日志记录和告警

---

## 故障排查

### 后端无法启动

```bash
# 查看日志
cat backend/server.log

# 检查端口占用
lsof -i:8001

# 检查依赖
pip install -r backend/requirements.txt
```

### 前端无法访问后端

1. 确认后端服务正在运行
2. 检查 CORS 配置
3. 确认 API 地址正确
4. 查看浏览器控制台错误

### 数据库错误

```bash
# 删除并重建数据库
rm data/assessments.db
# 重启后端服务
```
