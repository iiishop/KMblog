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
            <Tag v-for="tag in metadata.tags" :key="tag" :tagname="tag" />
          </div>
        </div>
      </div>
    </div>

    <!-- 文章内容 -->
    <p v-if="loadError" class="render-error" role="status">{{ loadError }}</p>
    <MarkdownContent v-if="markdownContent !== null" class="post-content" :content="markdownContent" @rendered="calculateStats" />

    <!-- 评论区域 -->
    <UtterancesComments v-if="metadata.title" :issueTitle="metadata.title" />

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
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import axios from 'axios';
import IconCategory from '@/components/icons/IconCategory.vue';
import IconDate from '@/components/icons/IconDate.vue';
import { parseMarkdownMetadataSync, resolvePostImage } from '@/utils';
import MarkdownContent from '@/components/MarkdownPanelComps/MarkdownContent.vue';
import UtterancesComments from '@/components/UtterancesComments.vue';
import Tag from '@/components/PostPanelComps/Tag.vue';

// 定义 props
const props = defineProps({
  markdownUrl: {
    type: String,
    default: ''
  },
  content: { type: String, default: null },
  scrollContainer: { type: Object, default: null },
  decryptedContent: {
    type: String,
    default: null
  }
});

const metadata = ref({});
const markdownContent = ref(null);
const loadError = ref('');
let loadRevision = 0;
let loadController;
const panelRef = ref(null);
const headerRef = ref(null);
const colorCanvas = ref(null);

// 阅读进度
const readingProgress = ref(0);
const showBackToTop = ref(false);

// 动态颜色
const dominantColor = ref(null);
const accentColor = ref(null);

// 文章统计
const articleStats = ref({
  wordCount: 0,
  readingTime: 0
});

// CSS变量
const cssVars = computed(() => {
  // 图片头图延续图片取色；没有图片或取色失败时采用主题中性色。
  if (!metadata.value.img || !dominantColor.value || !accentColor.value) return {};
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
    dominantColor.value = null;
    accentColor.value = null;
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
  if (!panelRef.value) return;

  const root = props.scrollContainer;
  const panelTop = root ? panelRef.value.getBoundingClientRect().top - root.getBoundingClientRect().top + root.scrollTop : panelRef.value.offsetTop;
  const panelHeight = panelRef.value.scrollHeight;
  const windowHeight = root ? root.clientHeight : window.innerHeight;
  const scrollY = root ? root.scrollTop : window.scrollY;

  // 计算阅读进度
  const scrolled = scrollY - panelTop;
  const totalScroll = panelHeight - windowHeight;
  const progress = totalScroll > 0 ? Math.min(Math.max((scrolled / totalScroll) * 100, 0), 100) : 0;
  readingProgress.value = progress;

  // 显示回到顶部按钮
  showBackToTop.value = scrollY > 500;
};

// 回到顶部
const scrollToTop = () => {
  (props.scrollContainer || window).scrollTo({
    top: 0,
    behavior: 'smooth'
  });
};

// A draft and a fetched article differ only in where their source comes from.
watch(() => [props.markdownUrl, props.content, props.decryptedContent], async ([url, draft, decrypted]) => {
  const current = ++loadRevision;
  loadController?.abort();
  loadController = new AbortController();
  readingProgress.value = 0;
  try {
    const markdown = draft ?? decrypted ?? (await axios.get(url, { signal: loadController.signal })).data;
    const { meta } = parseMarkdownMetadataSync(markdown);
    if (current !== loadRevision) return;
    const nextMetadata = { ...meta };
    nextMetadata.img = resolvePostImage(nextMetadata.img);
    if (nextMetadata.date) {
      const date = new Date(nextMetadata.date);
      if (!Number.isNaN(date.getTime())) {
        const hours = date.getHours();
        nextMetadata.date = date.toLocaleDateString().replace(/\//g, '月').replace('月', '年') + '日'
          + (hours < 6 ? ' 凌晨' : hours < 12 ? ' 上午' : hours < 18 ? ' 下午' : ' 晚上');
      }
    }
    if (metadata.value.img !== nextMetadata.img) {
      dominantColor.value = null;
      accentColor.value = null;
    }
    metadata.value = nextMetadata;
    markdownContent.value = markdown;
    loadError.value = '';
  } catch (error) {
    if (current === loadRevision && !loadController.signal.aborted) loadError.value = `预览暂未更新，请检查文章头部格式或文件连接：${error.message}`;
  }
}, { immediate: true });

watch(() => props.scrollContainer, (root, previous) => {
  (previous || window).removeEventListener('scroll', handleScroll);
  (root || window).addEventListener('scroll', handleScroll, { passive: true });
});
onMounted(() => (props.scrollContainer || window).addEventListener('scroll', handleScroll, { passive: true }));
onUnmounted(() => {
  loadRevision++;
  loadController?.abort();
  (props.scrollContainer || window).removeEventListener('scroll', handleScroll);
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
  background: var(--theme-reading);
  z-index: 10000;
  transition: width 0.15s ease-out;
  box-shadow: 0 2px 8px var(--theme-shadow-sm);
}

/* === 文章头部 === */
.post-header {
  position: relative;
  width: 100%;
  overflow: hidden;
  /* 保持头部的 overflow hidden */
  min-height: 300px;
  max-height: 500px;
  background: var(--gradient, var(--theme-index));
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
  color: var(--theme-content-text);
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

/* === 回到顶部按钮 === */
.back-to-top {
  position: fixed;
  bottom: 3rem;
  right: 3rem;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: var(--theme-button-bg);
  color: var(--theme-button-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px var(--theme-shadow-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.back-to-top:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 8px 24px var(--theme-shadow-lg);
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
