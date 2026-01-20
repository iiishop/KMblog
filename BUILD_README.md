# KMBlog 管理工具打包说明

## 安装依赖

```bash
# 安装 Flet
uv pip install flet

# 或使用 pip
pip install flet
```

## 运行 Flet GUI

```bash
python blog_manager.py
```

## 打包成 exe

### 方法 1: 使用 Flet 内置打包命令（推荐）

```bash
# 打包成独立的 exe 文件
flet pack blog_manager.py --name "KMBlog管理工具" --icon mainTools/icon.ico

# 不添加图标
flet pack blog_manager.py --name "KMBlog管理工具"
```

### 方法 2: 使用 PyInstaller

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --name "KMBlog管理工具" blog_manager.py
```

## 打包后的注意事项

1. **exe 位置**: 打包后的 exe 文件会在项目根目录的 `dist` 文件夹中
2. **运行位置**: 将 exe 文件移动到项目根目录（与 src 文件夹同级）
3. **路径处理**: 程序已自动处理路径问题，可以从根目录直接运行

## 目录结构

```
KMblog/
├── blog_manager.py          # Flet GUI 主程序（在根目录）
├── KMBlog管理工具.exe       # 打包后的 exe（放在根目录）
├── mainTools/               # 工具模块
│   ├── commands.py
│   ├── utility.py
│   ├── path_utils.py        # 路径工具
│   ├── main.py             # 命令行版本
│   └── gui.py              # Tkinter 版本
├── src/
│   ├── Posts/
│   │   ├── Markdowns/
│   │   └── Images/
│   └── assets/
│       ├── PostDirectory.json
│       ├── Tags.json
│       └── Categories.json
└── ...
```

## 使用说明

### GUI 版本功能

1. **命令按钮**: 点击命令按钮执行相应操作
2. **输入参数**: 
   - 文章名称: 用于添加或删除文章
   - 合集名称: 用于指定文章所属合集或删除合集
3. **输出区域**: 显示命令执行结果
4. **语言切换**: 点击右上角按钮切换中英文界面

### 双语支持

- 界面默认中文，可切换英文
- 所有按钮、标签、提示信息都支持双语
- 命令描述也会随语言切换

### 主要命令

- **InitBlog**: 初始化博客结构
- **Generate**: 生成 JSON 配置文件
- **AddPost**: 添加新文章
- **DeletePost**: 删除文章
- **DeleteCollection**: 删除合集
- **ListAllPosts**: 列出所有文章
- **ListCollections**: 列出所有合集
- **ShowPostsJson**: 显示文章目录 JSON
- **ShowTagsJson**: 显示标签 JSON
- **ShowCategoriesJson**: 显示分类 JSON

## 故障排除

### 打包错误

如果打包失败，尝试：
```bash
# 清理缓存
flet pack --clean blog_manager.py

# 或使用详细输出查看错误
flet pack --verbose blog_manager.py
```

### 路径错误

如果运行时提示找不到文件或目录：
1. 确保 exe 文件在项目根目录
2. 确保 src/Posts 目录存在
3. 运行 InitBlog 命令初始化结构

### Python 环境

建议使用 Python 3.8 或更高版本。
