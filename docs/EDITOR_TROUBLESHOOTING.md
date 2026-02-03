# 编辑器启动问题排查指南

## 常见错误

### 1. 开发服务器启动失败 (退出码: 4294963238)

**问题原因：**
- npm 未安装或不在 PATH 中
- node_modules 未安装
- package.json 不存在
- 端口被占用

**解决方案：** 见下方详细步骤

### 2. 等待服务器启动超时

**问题原因：**
- Python 解释器未找到或不可用
- editor_server.py 启动失败
- 防火墙阻止了服务器

**解决方案：** 见下方详细步骤

### 3. 打开新的 KMblogManager.exe

**问题原因：**
打包后的 exe 尝试使用自身启动 Python 脚本，导致循环启动。

**解决方案：**
已在最新版本中修复。如果仍有问题，请确保：
1. Python 已安装并在 PATH 中
2. 可以在命令行运行 `python --version`

---

## 详细解决方案

### 步骤 1: 检查 Python 是否安装

打开命令提示符（CMD）或 PowerShell，运行：

```bash
python --version
```

**预期输出：** `Python 3.9.x` 或更高版本

**如果提示"不是内部或外部命令"：**
1. 下载并安装 Python: https://www.python.org/downloads/
2. **重要：** 安装时勾选 "Add Python to PATH"
3. 安装完成后重启电脑
4. 再次运行 `python --version` 验证

### 步骤 2: 检查 Node.js 和 npm 是否安装

```bash
node --version
npm --version
```

**预期输出：** 显示版本号

**如果提示"不是内部或外部命令"：**
1. 下载并安装 Node.js: https://nodejs.org/
2. 推荐安装 LTS 版本
3. 安装完成后重启电脑
4. 再次验证

### 步骤 3: 检查 node_modules 是否存在

在博客目录（exe 所在目录）中，应该有一个 `node_modules` 文件夹。

**如果不存在：**

```bash
cd <博客目录>
npm install
```

### 步骤 4: 检查 package.json 是否存在

在博客目录中应该有 `package.json` 文件。

**如果不存在：**
1. 点击"初始化博客框架"按钮
2. 或手动从 GitHub 克隆：
   ```bash
   git clone https://github.com/iiishop/KMblog
   ```

### 步骤 5: 检查端口是否被占用

默认端口：
- 前端开发服务器: 5173
- 后端 API 服务器: 8000-8100（自动选择）

**Windows 检查端口：**
```bash
netstat -ano | findstr :5173
```

**如果端口被占用，杀死进程：**
```bash
taskkill /F /PID <进程ID>
```

**Linux/Mac 检查端口：**
```bash
lsof -i :5173
kill -9 <进程ID>
```

### 步骤 6: 手动测试

#### 测试前端开发服务器

在博客目录中运行：

```bash
npm run dev
```

**成功输出示例：**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

#### 测试后端 API 服务器

在博客目录中运行：

```bash
python mainTools/editor_server.py
```

**成功输出示例：**
```
INFO:     Started server process [xxxxx]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 目录结构检查

打包后的 exe 应该放在博客根目录中：

```
KMBlog/
├── KMblogManager.exe  ← exe 文件
├── package.json       ← 必需
├── node_modules/      ← 必需（运行 npm install 后生成）
├── src/               ← 必需
├── public/            ← 必需
├── mainTools/         ← 必需
├── vite.config.js     ← 必需
└── ...
```

---

## 调试模式

### 查看详细日志

在命令行中运行 exe，查看详细错误信息：

```bash
cd <博客目录>
KMblogManager.exe
```

查看控制台输出，特别是：
- `[Editor]` - 编辑器启动日志
- `[DEV SERVER]` - 前端开发服务器日志
- `[SERVER]` - 后端 API 服务器日志

### 检查 Python 依赖

编辑器后端需要以下 Python 包：

```bash
pip install fastapi uvicorn python-multipart
```

---

## 常见错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 4294963238 | 命令未找到 | npm 不在 PATH 中，重新安装 Node.js |
| 1 | 一般错误 | npm 命令执行失败，检查 package.json |
| 3221225786 | 访问被拒绝 | 权限问题，以管理员身份运行 |
| 超时 | 服务器启动超时 | Python 未找到或端口被占用 |

---

## 防火墙和杀毒软件

某些防火墙或杀毒软件可能阻止：
1. npm 下载依赖
2. node 启动开发服务器
3. Python 启动 API 服务器

**解决方案：**
1. 临时关闭防火墙/杀毒软件测试
2. 添加 exe、node.exe、python.exe 到白名单
3. 允许本地端口 5173 和 8000-8100

---

## 联系支持

如果以上方法都无法解决问题，请提供：

1. **完整的错误信息**（截图或复制文本）
2. **环境信息：**
   ```bash
   python --version
   node --version
   npm --version
   ```
3. **博客目录的文件列表：**
   ```bash
   dir  # Windows
   ls -la  # Linux/Mac
   ```
4. **手动测试输出：**
   ```bash
   npm run dev
   python mainTools/editor_server.py
   ```
5. **控制台日志**（运行 exe 时的完整输出）

---

## 快速检查清单

- [ ] Python 3.9+ 已安装并在 PATH 中
- [ ] Node.js 和 npm 已安装并在 PATH 中
- [ ] 博客目录包含 package.json
- [ ] 已运行 `npm install`，存在 node_modules 目录
- [ ] 端口 5173 和 8000-8100 未被占用
- [ ] 防火墙/杀毒软件未阻止
- [ ] exe 在博客根目录中运行
- [ ] 手动测试 `npm run dev` 成功
- [ ] 手动测试 `python mainTools/editor_server.py` 成功
