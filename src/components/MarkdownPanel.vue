<template>
  <div class="MarkdownPanel" ref="panelRef" :style="cssVars">
    <!-- 阅读进度条 -->
    <div class="reading-progress" :style="{ width: readingProgress + '%' }"></div>

    <!-- 文章头部 -->
    <div class="post-header" ref="headerRef">
      <div class="image-container">
        <img v-if="metadata.img" :src="metadata.img" alt="Post Image" class="header-image" crossorigin="anonymous"
          @load="extractColorsFromImage" />
        <canvas ref="colorCanvas" style="display: none;"></canvas>
        <div class="overlay">
          <div class="header-content">
            <h1 class="post-title">{{ metadata.title }}</h1>
            <div class="meta-info">
              <div class="category-panel" v-if="lastCategory">
                <IconCategory style="width: 1rem; height: 1rem;" />
                <router-link :to="categoryLink">{{ lastCategory }}</router-link>
              </div>
              <span class="meta-divider" v-if="lastCategory && metadata.date">•</span>
              <div class="date-panel" v-if="metadata.date">
                <IconDate style="width: 1rem; height: 1rem;" />
                <router-link :to="archiveLink">{{ metadata.date }}</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文章信息卡片 -->
    <div class="article-stats" v-if="articleStats.wordCount > 0">
      <div class="stat-item">
        <div class="stat-content">
          <span class="stat-label">字数</span>
          <span class="stat-value">{{ articleStats.wordCount.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <div class="stat-content">
          <span class="stat-label">阅读时间</span>
          <span class="stat-value">{{ articleStats.readingTime }} 分钟</span>
        </div>
      </div>
      <div class="stat-divider" v-if="metadata.tags && metadata.tags.length > 0"></div>
      <div class="stat-item stat-tags" v-if="metadata.tags && metadata.tags.length > 0">
        <div class="stat-content">
          <span class="stat-label">标签</span>
          <div class="tags-container">
            <span v-for="tag in metadata.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 文章内容 -->
    <article class="post-content markdown" ref="contentRef">
      <div v-html="htmlContent"></div>
    </article>

    <!-- 评论区 -->
    <div v-if="showComments" class="comments-section">
      <div class="comments-header">
        <h2 class="comments-title">💬 评论区</h2>
        <p class="comments-subtitle">欢迎留下你的想法和反馈</p>
      </div>
      <GiscusComments component-type="markdown" :term="commentTerm" :emphasize-reactions="true" />
    </div>

    <!-- 回到顶部按钮 -->
    <transition name="fade">
      <button v-if="showBackToTop" class="back-to-top" @click="scrollToTop">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 19V5M5 12l7-7 7 7" />
        </svg>
      </button>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick, defineAsyncComponent } from 'vue';
import axios from 'axios';
import fm from 'front-matter';
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import '@/components/MarkdownPanelComps/MarkdownStyle.css';
import mermaid from 'mermaid';
import IconCategory from '@/components/icons/IconCategory.vue';
import IconDate from '@/components/icons/IconDate.vue';
import config from '@/config';
import { renderDynamicComponents } from '@/components/MarkdownPanelComps/DynamicComponentRenderer.js';
import { parseMarkdownMetadata } from '@/utils';
import GiscusComments from '@/components/GiscusComments.vue';

// 使用 Vite 的代码分割功能进行动态导入
const SteamGameBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/SteamGameBlock.vue'));
const BangumiBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/BangumiBlock.vue'));
const BilibiliVideoBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/BilibiliVideoBlock.vue'));
const GithubRepoBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/GithubRepoBlock.vue'));
const XiaohongshuNoteBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/XiaohongshuNoteBlock.vue'));
const CarouselBlock = defineAsyncComponent(() => import('./MarkdownPanelComps/CarouselBlock.vue'));

// 定义 props
const props = defineProps({
  markdownUrl: {
    type: String,
    required: true
  },
  decryptedContent: {
    type: String,
    default: null
  }
});

const metadata = ref({});
const htmlContent = ref('');
const panelRef = ref(null);
const contentRef = ref(null);
const headerRef = ref(null);
const colorCanvas = ref(null);

// 阅读进度
const readingProgress = ref(0);
const showBackToTop = ref(false);

// 动态颜色
const dominantColor = ref({ h: 210, s: 70, l: 55 });
const accentColor = ref({ h: 220, s: 65, l: 50 });

// 文章统计
const articleStats = ref({
  wordCount: 0,
  readingTime: 0
});

// 评论相关
const showComments = computed(() => {
  return config.Giscus?.enabled && config.Giscus?.markdownPanel?.enabled;
});

const commentTerm = computed(() => {
  // Use article title or URL as unique identifier
  return metadata.value.title || props.markdownUrl;
});

// CSS变量
const cssVars = computed(() => {
  const { h, s, l } = dominantColor.value;
  const { h: h2, s: s2, l: l2 } = accentColor.value;

  return {
    '--primary-hue': h,
    '--primary-sat': s + '%',
    '--primary-light': l + '%',
    '--accent-hue': h2,
    '--accent-sat': s2 + '%',
    '--accent-light': l2 + '%',
    '--primary-color': `hsl(${h}, ${s}%, ${l}%)`,
    '--primary-light-color': `hsl(${h}, ${s}%, ${Math.min(l + 15, 85)}%)`,
    '--primary-dark-color': `hsl(${h}, ${s}%, ${Math.max(l - 15, 20)})`,
    '--accent-color': `hsl(${h2}, ${s2}%, ${l2}%)`,
    '--gradient': `linear-gradient(135deg, hsl(${h}, ${s}%, ${l}%) 0%, hsl(${h2}, ${s2}%, ${l2}%) 100%)`
  };
});

// 计算文章统计信息
const calculateStats = (content) => {
  // 移除 HTML 标签
  const textContent = content.replace(/<[^>]*>/g, '');
  // 统计字数（包括中英文）
  const wordCount = textContent.replace(/\s+/g, '').length;
  // 计算阅读时间（假设每分钟阅读 300 字）
  const readingTime = Math.ceil(wordCount / 300);

  articleStats.value = {
    wordCount,
    readingTime
  };
};

// 从图片提取主色调
const extractColorsFromImage = () => {
  const img = headerRef.value?.querySelector('.header-image');
  const canvas = colorCanvas.value;

  if (!img || !canvas) return;

  const ctx = canvas.getContext('2d');
  canvas.width = img.width;
  canvas.height = img.height;

  try {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

    // 采样像素（每隔10个像素采样一次以提高性能）
    const colorMap = new Map();
    for (let i = 0; i < imageData.length; i += 40) {
      const r = imageData[i];
      const g = imageData[i + 1];
      const b = imageData[i + 2];
      const a = imageData[i + 3];

      // 跳过透明或接近白色/黑色的像素
      if (a < 128 || (r > 240 && g > 240 && b > 240) || (r < 15 && g < 15 && b < 15)) continue;

      const hsl = rgbToHsl(r, g, b);
      // 只保留饱和度足够的颜色
      if (hsl.s > 20) {
        const key = `${Math.round(hsl.h / 10) * 10}-${Math.round(hsl.s / 10) * 10}`;
        colorMap.set(key, (colorMap.get(key) || 0) + 1);
      }
    }

    // 找出出现最多的颜色
    if (colorMap.size > 0) {
      const sortedColors = Array.from(colorMap.entries()).sort((a, b) => b[1] - a[1]);
      const [topColorKey] = sortedColors[0];
      const [h, s] = topColorKey.split('-').map(Number);

      dominantColor.value = { h, s: Math.min(s + 10, 80), l: 55 };

      // 生成互补色作为强调色
      if (sortedColors.length > 1) {
        const [accentColorKey] = sortedColors[1];
        const [h2, s2] = accentColorKey.split('-').map(Number);
        accentColor.value = { h: h2, s: Math.min(s2 + 5, 75), l: 50 };
      } else {
        accentColor.value = { h: (h + 30) % 360, s: Math.min(s + 5, 75), l: 50 };
      }
    }
  } catch (error) {
    console.warn('无法提取图片颜色，使用默认配色:', error);
    // 使用默认配色
    dominantColor.value = { h: 210, s: 70, l: 55 };
    accentColor.value = { h: 220, s: 65, l: 50 };
  }
};

// RGB转HSL
const rgbToHsl = (r, g, b) => {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }

  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  };
};

// 滚动处理
const handleScroll = () => {
  if (!contentRef.value || !panelRef.value) return;

  const panelTop = panelRef.value.offsetTop;
  const panelHeight = panelRef.value.scrollHeight;
  const windowHeight = window.innerHeight;
  const scrollY = window.scrollY;

  // 计算阅读进度
  const scrolled = scrollY - panelTop;
  const totalScroll = panelHeight - windowHeight;
  const progress = Math.min(Math.max((scrolled / totalScroll) * 100, 0), 100);
  readingProgress.value = progress;

  // 显示回到顶部按钮
  showBackToTop.value = scrollY > 500;
};

// 回到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

// 解析 Markdown 文件并提取 metadata 和内容
const parseMarkdown = async (url, decryptedText = null) => {
  try {
    let markdown;

    // 如果有解密后的内容，直接使用
    if (decryptedText) {
      markdown = decryptedText;
      console.log('使用解密后的内容');
    } else {
      // 否则从 URL 加载
      const response = await axios.get(url);
      markdown = response.data;
    }

    // 使用 front-matter 解析 metadata
    const { body } = fm(markdown);
    const { meta } = await parseMarkdownMetadata(markdown);
    metadata.value = meta;
    if (metadata.value.img) {
      metadata.value.img = `/Posts/Images/${metadata.value.img}`;
    }
    const date = new Date(metadata.value.date);
    const hours = date.getHours();

    // 格式化日期为 '年-月-日'
    metadata.value.date = date.toLocaleDateString().replace(/\//g, '月').replace('月', '年') + '日';

    // 添加时间段
    if (hours < 6) {
      metadata.value.date += ' 凌晨';
    } else if (hours < 12) {
      metadata.value.date += ' 上午';
    } else if (hours < 18) {
      metadata.value.date += ' 下午';
    } else {
      metadata.value.date += ' 晚上';
    }

    // 解析 Markdown 内容
    htmlContent.value = md.render(body);

    // 计算文章统计信息
    calculateStats(htmlContent.value);

    // 在 nextTick 中手动编译和挂载组件
    await nextTick();
    const container = contentRef.value;
    if (container) {
      renderDynamicComponents(container, {
        'steamgameblock': SteamGameBlock,
        'bangumiblock': BangumiBlock,
        'bilibilivideoblock': BilibiliVideoBlock,
        'githubrepoblock': GithubRepoBlock,
        'xiaohongshunoteblock': XiaohongshuNoteBlock,
        'carouselblock': CarouselBlock
      });
    }

    // 渲染 Mermaid 图表
    await nextTick();
    if (typeof mermaid !== 'undefined') {
      try {
        // 重置状态
        mermaid.mermaidAPI.reset();

        // 重新初始化并渲染
        await mermaid.run({
          nodes: document.querySelectorAll('.mermaid'),
        });

        // 修复渲染后的 SVG 尺寸，确保不超出容器
        await nextTick();
        const mermaidSvgs = document.querySelectorAll('.mermaid svg');
        mermaidSvgs.forEach(svg => {
          // 删除所有内联宽高属性，让 CSS 完全控制
          svg.removeAttribute('width');
          svg.removeAttribute('height');

          // 强制应用样式
          svg.style.width = '100%';
          svg.style.height = '400px';
          svg.style.maxWidth = '100%';
          svg.style.maxHeight = '400px';
          svg.style.display = 'block';
          svg.style.margin = '0 auto';

          // 移除可能导致超出的内联样式
          if (svg.getAttribute('style')) {
            const styleStr = svg.getAttribute('style');
            // 移除固定的 max-width 限制（如 max-width: 300px）
            svg.setAttribute('style', styleStr.replace(/max-width:\s*\d+px;?/gi, ''));
          }
        });
      } catch (error) {
        console.warn('Mermaid rendering failed:', error);
      }
    }
  } catch (error) {
    console.error('Error fetching or parsing markdown file:', error);
  }
};

// 监控 markdownUrl 和 decryptedContent 的变化
watch(() => [props.markdownUrl, props.decryptedContent], ([newUrl, newContent]) => {
  parseMarkdown(newUrl, newContent);
  // 重置滚动位置和颜色
  readingProgress.value = 0;
  dominantColor.value = { h: 210, s: 70, l: 55 };
  accentColor.value = { h: 220, s: 65, l: 50 };
}, { immediate: true });

onMounted(() => {
  parseMarkdown(props.markdownUrl, props.decryptedContent);
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

const lastCategory = computed(() => {
  if (metadata.value.categories && metadata.value.categories.length > 0) {
    return metadata.value.categories[metadata.value.categories.length - 1];
  }
  return '';
});

const categoryLink = computed(() => {
  if (metadata.value.categories && metadata.value.categories.length > 0) {
    const fullPath = metadata.value.categories.join('/');
    return { name: 'CategoryPage', params: { fullPath } };
  }
  return '#';
});

const archiveLink = computed(() => ({ name: 'ArchivePage' }));
</script>

<style scoped>
/* === 主容器 === */
.MarkdownPanel {
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--theme-content-bg);
  border-radius: 1rem;
  overflow: visible;
  /* 改为 visible 以支持 sticky 定位 */
  box-shadow: 0 4px 20px var(--theme-shadow-md);
  position: relative;
  animation: fadeIn 0.6s ease-out;
  transition: var(--theme-transition-colors);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* === 阅读进度条 === */
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--gradient);
  z-index: 10000;
  transition: width 0.15s ease-out;
  box-shadow: 0 2px 8px var(--primary-color);
}

/* === 文章头部 === */
.post-header {
  position: relative;
  width: 100%;
  overflow: hidden;
  /* 保持头部的 overflow hidden */
  min-height: 300px;
  max-height: 500px;
  background: var(--theme-gradient);
  transition: var(--theme-transition-colors);
  border-radius: 1rem 1rem 0 0;
  /* 添加顶部圆角 */
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 300px;
  max-height: 500px;
}

.header-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.post-header:hover .header-image {
  transform: scale(1.02);
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom,
      rgba(0, 0, 0, 0) 0%,
      rgba(0, 0, 0, 0.3) 40%,
      rgba(0, 0, 0, 0.7) 100%);
  display: flex;
  align-items: flex-end;
  padding: 3rem;
  transition: var(--theme-transition-colors);
}

.header-content {
  width: 100%;
  max-width: 900px;
  color: #ffffff;
  position: relative;
  z-index: 2;
}

.post-title {
  font-size: 2.8rem;
  font-weight: 800;
  line-height: 1.25;
  margin: 0 0 1.2rem 0;
  font-family: 'Noto Serif SC', 'Merriweather', Georgia, serif;
  letter-spacing: -0.5px;
  color: #ffffff;
  /* 多层文字阴影创建发光效果 */
  text-shadow:
    0 0 10px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 0, 0, 0.6),
    0 0 30px rgba(0, 0, 0, 0.4),
    0 2px 4px rgba(0, 0, 0, 0.9),
    0 4px 8px rgba(0, 0, 0, 0.7),
    0 8px 16px rgba(0, 0, 0, 0.5);
  /* 添加白色发光边缘 */
  -webkit-text-stroke: 1px rgba(255, 255, 255, 0.3);
  text-stroke: 1px rgba(255, 255, 255, 0.3);
  /* 确保文字在任何背景下都清晰可见 */
  filter: drop-shadow(0 0 8px rgba(0, 0, 0, 0.8)) drop-shadow(0 0 16px rgba(0, 0, 0, 0.6));
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.95rem;
}

.meta-divider {
  opacity: 0.9;
  font-weight: 300;
  color: #ffffff;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.8);
}

.category-panel,
.date-panel {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(15px);
  border-radius: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  /* 添加发光效果 */
  box-shadow:
    0 0 20px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.category-panel:hover,
.date-panel:hover {
  background: rgba(0, 0, 0, 0.6);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow:
    0 4px 25px rgba(0, 0, 0, 0.6),
    0 0 30px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.category-panel a,
.date-panel a {
  text-decoration: none;
  color: #ffffff;
  font-weight: 600;
  transition: all 0.3s ease;
  /* 添加文字发光效果 */
  text-shadow:
    0 0 8px rgba(0, 0, 0, 0.8),
    0 1px 2px rgba(0, 0, 0, 0.9);
}

.category-panel a:hover,
.date-panel a:hover {
  color: #ffffff;
  text-shadow:
    0 0 12px rgba(255, 255, 255, 0.3),
    0 0 8px rgba(0, 0, 0, 0.8),
    0 1px 2px rgba(0, 0, 0, 0.9);
}

/* 图标也需要高对比度处理 */
.category-panel svg,
.date-panel svg {
  filter: drop-shadow(0 0 4px rgba(0, 0, 0, 0.8)) drop-shadow(0 1px 2px rgba(0, 0, 0, 0.9));
  color: #ffffff;
}

/* === 文章统计信息 === */
.article-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  padding: 2rem;
  background: var(--theme-content-bg);
  border-bottom: 1px solid var(--theme-content-border);
  transition: var(--theme-transition-colors);
  gap: 1rem 2rem;
  /* 行间距 列间距 */
}

.stat-item {
  flex: 0 0 auto;
  padding: 0 1.5rem;
  min-width: 120px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--theme-meta-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: var(--theme-transition-colors);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  font-variant-numeric: tabular-nums;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(to bottom,
      transparent,
      var(--theme-border-light),
      transparent);
  transition: var(--theme-transition-colors);
  flex-shrink: 0;
}

/* 两行布局：第一行显示字数和阅读时间，第二行显示标签 */
.stat-tags {
  flex-basis: 100%;
  margin-top: 0.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--theme-content-border);
}

.stat-tags .stat-content {
  flex-direction: row;
  gap: 0.8rem;
  justify-content: center;
}

.tags-container {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.tag {
  padding: 0.4rem 1rem;
  background: var(--theme-gradient);
  color: var(--theme-button-text);
  border-radius: 1.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: default;
}

.tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--primary-color);
  opacity: 0.9;
}

/* === 文章内容 === */
.post-content {
  padding: 3rem 4rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  line-height: 1.8;
  color: var(--theme-content-text);
  font-size: 1.05rem;
  transition: var(--theme-transition-colors);
}

/* === 评论区 - 专业长文风格 === */
.comments-section {
  width: 100%;
  margin: 0 auto;
  padding: 4rem 4rem 3rem;
  border-top: 2px solid var(--theme-content-border);
  background: linear-gradient(180deg,
      var(--theme-panel-bg) 0%,
      var(--theme-content-bg) 100%);
  transition: var(--theme-transition-colors);
  position: relative;
}

.comments-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: var(--theme-gradient);
  border-radius: 2px;
}

.comments-header {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--theme-border-light);
  position: relative;
}

.comments-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--theme-content-text);
  margin: 0 0 0.75rem 0;
  font-family: 'Noto Serif SC', 'Merriweather', Georgia, serif;
  background: var(--theme-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
}

.comments-subtitle {
  font-size: 1rem;
  color: var(--theme-meta-text);
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.02em;
}

/* === Giscus 专业风格定制 === */
.comments-section :deep(.gsc-main) {
  background: transparent !important;
  border: none !important;
}

.comments-section :deep(.gsc-comment-box) {
  background: var(--theme-panel-bg) !important;
  border: 2px solid var(--theme-border-light) !important;
  border-radius: 16px !important;
  padding: 1.5rem !important;
  margin-bottom: 2rem !important;
  box-shadow: 0 4px 16px var(--theme-shadow-sm) !important;
  transition: all 0.3s ease !important;
}

.comments-section :deep(.gsc-comment-box:hover) {
  border-color: var(--primary-color) !important;
  box-shadow: 0 8px 24px var(--theme-shadow-md) !important;
}

.comments-section :deep(.gsc-comment-box-tabs) {
  border-bottom: 2px solid var(--theme-border-light) !important;
  margin-bottom: 1rem !important;
}

.comments-section :deep(.gsc-comment-box-tab) {
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  padding: 0.75rem 1.5rem !important;
  color: var(--theme-meta-text) !important;
  border-radius: 8px 8px 0 0 !important;
  transition: all 0.3s ease !important;
}

.comments-section :deep(.gsc-comment-box-tab[aria-selected="true"]) {
  color: var(--primary-color) !important;
  background: var(--theme-surface-hover) !important;
  border-bottom: 3px solid var(--primary-color) !important;
}

.comments-section :deep(.gsc-comment-box-textarea) {
  background: var(--theme-content-bg) !important;
  border: 2px solid var(--theme-border-light) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
  font-size: 1rem !important;
  line-height: 1.6 !important;
  color: var(--theme-content-text) !important;
  transition: all 0.3s ease !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.comments-section :deep(.gsc-comment-box-textarea:focus) {
  border-color: var(--primary-color) !important;
  box-shadow: 0 0 0 3px var(--primary-light-color) !important;
  outline: none !important;
}

.comments-section :deep(.gsc-comment-box-bottom) {
  margin-top: 1rem !important;
  padding-top: 1rem !important;
  border-top: 1px solid var(--theme-border-light) !important;
}

.comments-section :deep(.gsc-comment-box-buttons) {
  gap: 0.75rem !important;
}

.comments-section :deep(.gsc-comment-box-button) {
  padding: 0.75rem 1.5rem !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  transition: all 0.3s ease !important;
  border: 2px solid transparent !important;
}

.comments-section :deep(.gsc-comment-box-button-primary) {
  background: var(--gradient) !important;
  color: var(--theme-button-text) !important;
  box-shadow: 0 4px 12px var(--primary-color) !important;
}

.comments-section :deep(.gsc-comment-box-button-primary:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px var(--primary-color) !important;
}

.comments-section :deep(.gsc-comment) {
  background: var(--theme-panel-bg) !important;
  border: 1px solid var(--theme-border-light) !important;
  border-radius: 16px !important;
  padding: 1.5rem !important;
  margin-bottom: 1.5rem !important;
  transition: all 0.3s ease !important;
}

.comments-section :deep(.gsc-comment:hover) {
  border-color: var(--theme-border-medium) !important;
  box-shadow: 0 4px 16px var(--theme-shadow-sm) !important;
  transform: translateY(-2px) !important;
}

.comments-section :deep(.gsc-comment-author) {
  font-weight: 600 !important;
  font-size: 1rem !important;
  color: var(--theme-content-text) !important;
}

.comments-section :deep(.gsc-comment-author-avatar) {
  border-radius: 12px !important;
  border: 2px solid var(--theme-border-light) !important;
}

.comments-section :deep(.gsc-comment-content) {
  color: var(--theme-content-text) !important;
  font-size: 0.95rem !important;
  line-height: 1.7 !important;
  margin-top: 1rem !important;
}

.comments-section :deep(.gsc-comment-reactions) {
  margin-top: 1rem !important;
  padding-top: 1rem !important;
  border-top: 1px solid var(--theme-border-light) !important;
}

.comments-section :deep(.gsc-reaction-button) {
  border-radius: 8px !important;
  padding: 0.5rem 0.75rem !important;
  background: var(--theme-surface-hover) !important;
  border: 1px solid var(--theme-border-light) !important;
  transition: all 0.3s ease !important;
}

.comments-section :deep(.gsc-reaction-button:hover) {
  background: var(--theme-surface-active) !important;
  border-color: var(--primary-color) !important;
  transform: scale(1.05) !important;
}

.comments-section :deep(.gsc-reactions-count) {
  font-weight: 600 !important;
  color: var(--primary-color) !important;
}

/* === 回到顶部按钮 === */
.back-to-top {
  position: fixed;
  bottom: 3rem;
  right: 3rem;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: var(--theme-gradient);
  color: var(--theme-button-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px var(--theme-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.back-to-top:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 24px var(--theme-primary);
}

.back-to-top:active {
  transform: translateY(-2px) scale(1.02);
}

.back-to-top svg {
  width: 22px;
  height: 22px;
  transition: transform 0.3s ease;
}

.back-to-top:hover svg {
  transform: translateY(-2px);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: scale(0.8) rotate(-90deg);
}

.fade-leave-to {
  opacity: 0;
  transform: scale(0.8) rotate(90deg);
}

/* === 响应式设计 === */
@media (max-width: 1200px) {
  .article-stats {
    padding: 1.8rem;
    gap: 0.8rem 1.5rem;
  }

  .stat-item {
    padding: 0 1rem;
  }

  .stat-value {
    font-size: 1.4rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }
}

@media (max-width: 968px) {
  .post-title {
    font-size: 2.2rem;
  }

  .overlay {
    padding: 2rem;
  }

  .article-stats {
    padding: 2rem 1.5rem;
    gap: 1rem 1rem;
  }

  .stat-item {
    padding: 0 0.8rem;
    min-width: 100px;
  }

  .stat-tags {
    margin-top: 0.5rem;
    padding-top: 1rem;
  }

  .post-content {
    padding: 2rem 1.5rem;
  }

  .comments-section {
    padding: 2rem 1.5rem;
  }

  .comments-title {
    font-size: 1.5rem;
  }
}

/* 中等屏幕优化 (769px - 968px) - 保持两行布局 */
@media (max-width: 968px) and (min-width: 769px) {
  .article-stats {
    gap: 1rem 1.2rem;
  }

  .stat-item {
    min-width: 110px;
  }

  .stat-divider {
    height: 35px;
  }
}

/* 小平板优化 (641px - 768px) - 两行布局，第一行居中 */
@media (max-width: 768px) and (min-width: 641px) {
  .article-stats {
    padding: 1.8rem;
    gap: 1rem;
    justify-content: center;
  }

  .stat-item {
    padding: 0.8rem 1rem;
    background: var(--theme-surface-default);
    border-radius: 12px;
    border: 1px solid var(--theme-border-light);
    min-width: 0;
    flex: 0 0 auto;
  }

  .stat-divider {
    display: none;
  }

  .stat-tags {
    background: none;
    border: none;
    padding-top: 1rem;
    margin-top: 0.5rem;
  }

  .stat-tags .stat-content {
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .post-title {
    font-size: 1.8rem;
  }

  .overlay {
    padding: 1.5rem;
  }

  .meta-info {
    font-size: 0.9rem;
  }

  .article-stats {
    padding: 1.5rem;
    flex-direction: column;
    gap: 1.5rem;
    align-items: stretch;
  }

  .stat-item {
    padding: 0;
    background: none;
    border: none;
    border-bottom: 1px solid var(--theme-content-border);
    padding-bottom: 1.5rem;
    border-radius: 0;
    min-width: 0;
    flex: none;
  }

  .stat-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .stat-divider {
    display: none;
  }

  .stat-tags {
    border-top: none;
    padding-top: 0;
    margin-top: 0;
  }

  .stat-tags .stat-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .tags-container {
    justify-content: flex-start;
  }

  .stat-value {
    font-size: 1.3rem;
  }

  .post-content {
    padding: 1.5rem 1rem;
    font-size: 1rem;
  }

  .comments-section {
    padding: 1.5rem 1rem;
  }

  .comments-title {
    font-size: 1.3rem;
  }

  .comments-subtitle {
    font-size: 0.85rem;
  }

  .back-to-top {
    bottom: 1.5rem;
    right: 1.5rem;
    width: 46px;
    height: 46px;
  }

  .back-to-top svg {
    width: 20px;
    height: 20px;
  }
}
</style>
