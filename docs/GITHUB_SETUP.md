# GitHub 仓库设置指南

## 步骤 1: 在 GitHub 创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `standards-assessment` (或你喜欢的名字)
   - **Description**: 标准自评估系统 - 网络安全、数据安全合规评估平台
   - **Visibility**: Public (公开) 或 Private (私有)
   - **不要** 勾选 "Add a README file"
   - **不要** 勾选 ".gitignore"
   - **不要** 选择许可证
3. 点击 "Create repository"

## 步骤 2: 关联本地仓库并推送

在终端执行以下命令（替换 YOUR_USERNAME 为你的 GitHub 用户名）：

```bash
cd /home/admin/openclaw/workspace/standards-assessment

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/standards-assessment.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

如果遇到认证问题，可以使用 Personal Access Token：

```bash
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/standards-assessment.git
git push -u origin main
```

## 步骤 3: 启用 GitHub Pages

1. 进入你的 GitHub 仓库页面
2. 点击 **Settings** (设置)
3. 左侧菜单选择 **Pages**
4. 在 "Build and deployment" 部分：
   - **Source**: Deploy from a branch
   - **Branch**: 选择 `gh-pages` (如果没有，先创建)
   - **Folder**: `/ (root)`
5. 点击 **Save**

## 步骤 4: 推送前端到 gh-pages 分支

```bash
cd /home/admin/openclaw/workspace/standards-assessment

# 使用 git subtree 推送前端目录
git subtree push --prefix frontend origin gh-pages
```

或者使用完整方式：

```bash
# 创建并切换到 gh-pages 分支
git checkout --orphan gh-pages

# 只保留前端文件
git rm -rf .
git checkout master -- frontend/
git mv frontend/* .
rm -rf frontend

# 修改 API 地址（如果需要）
# 编辑 index.html，将 API_BASE 改为你部署的后端地址

# 提交并推送
git add .
git commit -m "Deploy frontend to GitHub Pages"
git push -u origin gh-pages

# 返回主分支
git checkout master
```

## 步骤 5: 访问你的网站

GitHub Pages 部署完成后（通常需要 1-2 分钟），访问：

```
https://YOUR_USERNAME.github.io/standards-assessment/
```

## 注意事项

### 后端部署

GitHub Pages 只能托管静态文件（前端），后端需要单独部署：

**选项 A: 修改前端 API 地址**

编辑 `frontend/index.html`，找到：
```javascript
const API_BASE = 'http://localhost:8001/api';
```

修改为你的后端地址：
```javascript
const API_BASE = 'https://your-backend-url.com/api';
```

**选项 B: 部署后端到云平台**

推荐平台：
- [Railway](https://railway.app/) - 免费额度，简单易用
- [Render](https://render.com/) - 免费层，支持 Python
- [Hugging Face Spaces](https://huggingface.co/spaces) - 免费，支持 Gradio/Streamlit

### 本地测试

在推送之前，建议先在本地测试：

```bash
# 启动系统
./start.sh

# 访问 http://localhost:8080 测试所有功能
```

## 常见问题

### Q: 推送时提示权限错误？
A: 确保你有仓库的写入权限，或使用 Personal Access Token。

### Q: GitHub Pages 显示 404？
A: 等待 1-2 分钟，GitHub 需要时间构建。检查 Settings > Pages 确认配置正确。

### Q: 前端无法连接后端？
A: 确保 `API_BASE` 地址正确，并且后端服务允许跨域访问（CORS）。

### Q: 如何更新部署？
A: 修改代码后，重新执行 `git subtree push --prefix frontend origin gh-pages`

## 创建 Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 填写备注（如：standards-assessment-deploy）
4. 选择 scopes：勾选 `repo` (完整控制)
5. 点击 "Generate token"
6. **复制并保存 token**（只会显示一次）

使用 token 推送：
```bash
git push https://YOUR_USERNAME:TOKEN@github.com/YOUR_USERNAME/standards-assessment.git main
```
