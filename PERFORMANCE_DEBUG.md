# 性能调试指南

## 🔍 问题：切换页面后滚动卡顿

### 方法 1: 使用内置性能监控工具

#### 启动监控
在浏览器控制台输入：
```javascript
// 导入并启动监控
import perfMonitor from './src/utils/performanceMonitor.js'
perfMonitor.start()

// 或者直接使用全局对象（在 main.js 中导入后）
window.perfMonitor.start()
```

#### 停止监控
```javascript
window.perfMonitor.stop()
```

监控面板会实时显示：
- **FPS**: 帧率（应该 >55）
- **滚动事件**: 每秒触发次数
- **内存使用**: JS 堆内存
- **DOM 节点数**: 页面元素总数
- **长任务**: 超过 50ms 的任务

---

### 方法 2: Chrome DevTools Performance 分析

#### 步骤：
1. 打开 Chrome DevTools (F12)
2. 切换到 **Performance** 标签
3. 点击 **录制按钮** (圆圈图标)
4. 在页面上执行以下操作：
   - 切换到下一页
   - 等待动画完成
   - **上下滚动页面**（重现卡顿）
5. 停止录制

#### 查看分析：
- **FPS 图表**: 查看是否有掉帧（红色/黄色条）
- **Main 线程**: 查找长条状的黄色块（长任务）
- **Frames**: 点击卡顿的帧，查看调用栈
- **Bottom-Up**: 按耗时排序，找出最慢的函数

#### 重点关注：
- `animateParticles` - 粒子动画
- `onEnter/onLeave` - GSAP 过渡动画
- `Recalculate Style` - CSS 样式计算
- `Layout` - 页面布局重排
- `Paint` - 页面重绘

---

### 方法 3: 使用 Chrome Rendering 工具

#### 启用渲染分析：
1. 按 `Ctrl+Shift+P` (Windows) 或 `Cmd+Shift+P` (Mac)
2. 输入 "Show Rendering"
3. 勾选以下选项：

**关键选项：**
- ✅ **Paint flashing**: 高亮重绘区域（绿色闪烁）
- ✅ **Layout Shift Regions**: 布局偏移区域（蓝色）
- ✅ **Layer borders**: 显示合成层边界
- ✅ **Frame Rendering Stats**: 实时 FPS 显示

#### 测试：
- 切换页面并滚动
- 观察是否有大面积绿色闪烁（频繁重绘）
- 检查 FPS 数值

---

### 方法 4: 检查特定问题

#### 1. 检查 GSAP 动画是否持续影响
在控制台运行：
```javascript
// 查看当前运行的 GSAP 动画
gsap.globalTimeline.getChildren()

// 停止所有动画测试
gsap.globalTimeline.pause()
// 然后滚动看是否还卡顿
```

#### 2. 检查是否是 Vue 响应式问题
```javascript
// 在 PostPanel.vue 的 displayedPosts computed 中添加日志
watch(displayedPosts, (newVal) => {
    console.log('displayedPosts changed:', newVal.length)
})
```

#### 3. 检查是否是图片加载问题
```javascript
// 统计未加载完成的图片
const images = document.querySelectorAll('img')
const loading = Array.from(images).filter(img => !img.complete)
console.log('加载中的图片数量:', loading.length)
```

#### 4. 检查事件监听器数量
```javascript
// 使用 Chrome DevTools
// Elements 标签 -> Event Listeners 面板
// 查看 scroll 事件监听器数量
```

---

### 方法 5: 定位具体组件

#### 临时禁用组件测试：
在 `PostPanel.vue` 中逐个注释组件：

```vue
<!-- 测试 1: 禁用过渡动画 -->
<TransitionGroup name="list" tag="div" class="posts">
  <!-- 改为 -->
<div class="posts">

<!-- 测试 2: 禁用粒子效果 -->
<!-- 在 Post.vue 中直接 return -->
function handleMouseEnter() {
    return; // 禁用粒子
}

<!-- 测试 3: 禁用图片 -->
<div class="image-panel" v-if="false">
```

每次禁用后测试滚动性能，定位问题组件。

---

## 📊 预期结果

### 正常性能指标：
- FPS: **55-60**
- 滚动事件: **<60/s**（有节流）
- 长任务: **0-2 个/页面切换**
- Paint 面积: **<30% 可见区域**

### 问题指标：
- FPS: **<30**（卡顿）
- 长任务: **>5 个且 >100ms**
- 连续重绘: **整个页面闪绿色**

---

## 🎯 可能的问题点

根据已优化的代码，剩余可能的问题：

1. **GSAP clearProps 未生效** - 内联样式累积
2. **Collection 主题图片加载** - 大图片阻塞渲染
3. **过渡动画期间的 DOM 操作** - TransitionGroup 内部实现
4. **其他组件干扰** - BaseLayout、HeadMenu 等
5. **浏览器扩展冲突** - 在隐身模式测试

---

## 💡 快速排查命令

```javascript
// 一键诊断脚本
(function() {
    const stats = {
        fps: 0,
        images: document.querySelectorAll('img').length,
        incompleteImages: Array.from(document.querySelectorAll('img')).filter(i => !i.complete).length,
        domNodes: document.querySelectorAll('*').length,
        eventListeners: window.getEventListeners ? Object.keys(getEventListeners(window)).length : 'N/A',
        gsapAnimations: typeof gsap !== 'undefined' ? gsap.globalTimeline.getChildren().length : 0,
        memory: performance.memory ? (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + 'MB' : 'N/A'
    };
    
    console.table(stats);
    console.log('建议：');
    if (stats.incompleteImages > 5) console.log('⚠️ 有', stats.incompleteImages, '张图片未加载完成');
    if (stats.domNodes > 3000) console.log('⚠️ DOM 节点过多:', stats.domNodes);
    if (stats.gsapAnimations > 0) console.log('⚠️ GSAP 仍有', stats.gsapAnimations, '个动画在运行');
})();
```

---

## 下一步行动

1. **先运行快速诊断脚本**
2. **启用性能监控工具** (`perfMonitor.start()`)
3. **录制 Performance 分析** - 找到最慢的函数
4. **根据发现针对性优化**

需要我帮你集成性能监控工具到项目中吗？
