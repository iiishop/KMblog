# Giscus 快速配置（5分钟搞定）

## 第一步：准备仓库（2分钟）

1. 确保你的博客仓库是**公开的**（Public）

2. 启用 Discussions：
   - 进入仓库 → Settings → Features
   - 勾选 ✅ Discussions

3. 安装 Giscus App：
   - 访问 https://github.com/apps/giscus
   - 点击 Install
   - 选择你的博客仓库

## 第二步：获取配置（2分钟）

访问 https://giscus.app/zh-CN

1. **输入仓库**：`你的用户名/仓库名`
   ```
   例如：iiishop/KMblog
   ```

2. **页面映射**：选择 `pathname`（推荐）

3. **Discussion 分类**：选择 `Announcements`

4. **特性**：
   - ✅ 启用主评论区上方的反应
   - ✅ 懒加载评论

5. **主题**：选择 `preferred_color_scheme`

6. **复制配置**：页面底部会显示你的配置信息

## 第三步：配置博客（1分钟）

### 方式 1：使用博客管理工具（推荐 ⭐）

1. 运行 `blog_manager.py` 或 `KMblogManager.exe`
2. 进入 **配置管理** (Settings) 页面
3. 滚动到 **Giscus 评论系统** 部分
4. 点击 **打开 Giscus 配置页面** 按钮（如果还没获取配置）
5. 将从 giscus.app 复制的**完整 `<script>` 标签**粘贴到文本框中
6. 点击 **应用配置** 按钮
7. 看到 "✅ Giscus 配置已保存！" 即表示成功

### 方式 2：手动编辑配置文件

打开 `src/giscus.config.js`，将从 giscus.app 复制的 `<script>` 标签粘贴到 `GISCUS_SCRIPT` 变量中：

```javascript
const GISCUS_SCRIPT = `
<script src="https://giscus.app/client.js"
        data-repo="你的用户名/仓库名"
        data-repo-id="R_kgDOxxxxxxx"
        data-category="Announcements"
        data-category-id="DIC_kwDOxxxxxxx"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="zh-CN"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
</script>
`;
```

系统会自动解析 `data-*` 属性并应用配置。

## 完成！

重启开发服务器或重新构建：

```bash
npm run dev
```

打开任意文章，滚动到底部，你就能看到评论区了！

## 常见问题

**Q: 评论区不显示？**
- 检查仓库是否公开
- 确认已安装 giscus app
- 检查 `repo` 和 `repoId` 是否正确

**Q: 只想在文章页面显示评论？**
```javascript
imageModal: {
    enabled: false,  // 禁用图片评论
}
```

**Q: 想要英文界面？**
```javascript
lang: 'en',
```

## 更多配置

查看完整文档：[GISCUS_SETUP.md](./GISCUS_SETUP.md)
