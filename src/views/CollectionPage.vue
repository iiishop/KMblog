<template>
    <BaseLayout :showTipList="false" :showInfoList="false">
        <template #main>
            <!-- 优雅的返回按钮 - 固定在左上角 -->
            <button class="elegant-back-button" @click="goBack" :title="'返回'">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                </svg>
                <span class="back-text">返回</span>
            </button>

            <div class="collection-archive" :class="{ 'page-ready': isPageReady }">
                <!-- 沉浸式封面区域 -->
                <div class="hero-section" :style="heroStyle">
                    <div class="hero-overlay"></div>
                    <div class="hero-content">

                        <div class="collection-meta">
                            <h1 class="collection-title">{{ collectionName }}</h1>
                            <div class="collection-stats">
                                <span class="stat-item">
                                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                        <path
                                            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                                    </svg>
                                    {{ articles.length }} 篇文章
                                </span>
                                <span class="stat-item">
                                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                        <path
                                            d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z" />
                                    </svg>
                                    {{ collectionDate }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <!-- 滚动提示 -->
                    <div class="scroll-indicator">
                        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <path d="M12 5v14M19 12l-7 7-7-7" />
                        </svg>
                    </div>
                </div>

                <!-- 文章时间轴 -->
                <div class="timeline-container">
                    <div class="timeline-line"></div>

                    <TransitionGroup name="article-list" appear>
                        <article v-for="(article, index) in articles" :key="article.id" class="article-card"
                            :style="{ '--index': index }" @click="navigateToArticle(article.path)">
                            <div class="timeline-dot"></div>

                            <div class="card-content">
                                <div class="card-header">
                                    <h2 class="article-title">{{ article.title }}</h2>
                                    <time class="article-date">{{ article.date }}</time>
                                </div>

                                <p v-if="article.pre" class="article-preview">{{ article.pre }}</p>

                                <div class="article-meta">
                                    <div v-if="article.tags && article.tags.length" class="tags">
                                        <span v-for="tag in article.tags.slice(0, 3)" :key="tag" class="tag">
                                            {{ tag }}
                                        </span>
                                    </div>

                                    <div class="read-more">
                                        <span>阅读全文</span>
                                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path d="M5 12h14M12 5l7 7-7 7" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </article>
                    </TransitionGroup>
                </div>
            </div>
        </template>
    </BaseLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseLayout from '@/views/BaseLayout.vue';
import globalVar from '@/globalVar.js';
import { parseMarkdownMetadata } from '@/utils.js';
import axios from 'axios';

// 接收路由传递的 props
const props = defineProps({
    collectionName: String
});

const route = useRoute();
const router = useRouter();

const collectionName = ref('');
const collectionDate = ref('');
const collectionImage = ref('');
const articles = ref([]);
const dominantColor = ref('rgba(102, 126, 234, 0.3)');
const isPageReady = ref(false);

// 动态 Hero 样式
const heroStyle = computed(() => ({
    backgroundImage: `url(${collectionImage.value})`,
    '--dominant-color': dominantColor.value
}));

// 返回上一页
const goBack = () => {
    router.back();
};

// 导航到文章
const navigateToArticle = (path) => {
    // 解析路径：/Posts/Collection/filename.md
    // 移除开头的 / 并分割
    const parts = path.replace(/^\//, '').split('/');

    // parts[0] = 'Posts'
    // parts[1] = collection name (可能不存在)
    // parts[2] = filename.md (或 parts[1] 如果没有 collection)

    let collection = null;
    let filename = '';

    if (parts.length >= 3) {
        // /Posts/Collection/file.md
        collection = parts[1];
        filename = parts[2];
    } else if (parts.length === 2) {
        // /Posts/file.md (没有 collection)
        filename = parts[1];
    }

    // 移除 .md 扩展名
    const mdName = filename.replace('.md', '');

    console.log('[CollectionPage] Navigating to article:', { path, collection, mdName });

    // 使用路由参数导航
    if (collection) {
        router.push({
            name: 'PostPage',
            params: { collection, mdName }
        });
    } else {
        router.push({
            name: 'PostPage',
            params: { mdName }
        });
    }
};

// 提取图片主色调
const extractDominantColor = async (imageUrl) => {
    return new Promise((resolve) => {
        const img = new Image();

        img.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                const colors = [];

                // 采样像素（每隔10个像素采样一次以提高性能）
                for (let i = 0; i < imageData.length; i += 40) {
                    const r = imageData[i];
                    const g = imageData[i + 1];
                    const b = imageData[i + 2];

                    // 忽略过亮的颜色
                    if (r < 240 || g < 240 || b < 240) {
                        colors.push([r, g, b]);
                    }
                }

                if (colors.length > 0) {
                    const avg = colors.reduce((acc, color) => {
                        return [acc[0] + color[0], acc[1] + color[1], acc[2] + color[2]];
                    }, [0, 0, 0]).map(c => Math.round(c / colors.length));

                    resolve(`rgba(${avg[0]}, ${avg[1]}, ${avg[2]}, 0.3)`);
                } else {
                    resolve('rgba(102, 126, 234, 0.3)');
                }
            } catch (error) {
                // 如果 canvas 操作失败（CORS 问题），使用默认颜色
                console.warn('Cannot extract color from image (CORS):', error);
                resolve('rgba(102, 126, 234, 0.3)');
            }
        };

        img.onerror = () => {
            console.warn('Error loading image for color extraction');
            resolve('rgba(102, 126, 234, 0.3)');
        };

        // 不设置 crossOrigin，避免 CORS 问题
        img.src = imageUrl;
    });
};

// 加载合集数据
onMounted(async () => {
    console.log('[CollectionPage] Component mounted');
    console.log('[CollectionPage] Props collectionName:', props.collectionName);
    console.log('[CollectionPage] Route params:', route.params);

    // 页面入场动画延迟
    setTimeout(() => {
        isPageReady.value = true;
    }, 100);

    // 优先使用 props，然后是 route.params
    const name = props.collectionName || route.params.name;
    console.log('[CollectionPage] Collection name:', name);

    if (!name) {
        console.error('[CollectionPage] No collection name found, redirecting to home');
        router.push('/');
        return;
    }

    collectionName.value = name;

    // 从 globalVar 获取合集信息
    console.log('[CollectionPage] globalVar.collections:', globalVar.collections);
    const collection = globalVar.collections[name];
    console.log('[CollectionPage] Collection data:', collection);

    if (collection) {
        collectionDate.value = collection.date;
        collectionImage.value = collection.image;

        // 提取主色调
        if (collection.image) {
            dominantColor.value = await extractDominantColor(collection.image);
        }
    }

    // 从 PostDirectory.json 获取文章列表
    try {
        const postDirResponse = await axios.get('/assets/PostDirectory.json');
        const postDirectory = postDirResponse.data;
        console.log('[CollectionPage] PostDirectory loaded:', postDirectory);

        if (postDirectory[name] && postDirectory[name].Markdowns) {
            const markdownPaths = postDirectory[name].Markdowns;
            console.log('[CollectionPage] Found markdowns:', markdownPaths);

            // 加载每篇文章的元数据
            const articlePromises = markdownPaths.map(async (item) => {
                try {
                    const response = await axios.get(item.path);
                    const metadata = await parseMarkdownMetadata(response.data);

                    console.log('[CollectionPage] Article metadata:', {
                        path: item.path,
                        metadata: metadata
                    });

                    return {
                        id: item.id,
                        path: item.path,
                        title: metadata.meta?.title || metadata.title || '无标题',
                        date: metadata.meta?.date || metadata.date || '',
                        pre: metadata.meta?.pre || metadata.pre || '',
                        tags: metadata.meta?.tags || metadata.tags || [],
                        categories: metadata.meta?.categories || metadata.categories || []
                    };
                } catch (error) {
                    console.error(`Failed to load article: ${item.path}`, error);
                    return null;
                }
            });

            const loadedArticles = await Promise.all(articlePromises);
            articles.value = loadedArticles.filter(a => a !== null)
                .sort((a, b) => new Date(b.date) - new Date(a.date)); // 按日期降序排列

            console.log('[CollectionPage] Loaded articles:', articles.value);
        } else {
            console.warn('[CollectionPage] No markdowns found for collection:', name);
            console.log('[CollectionPage] Available collections in postDirectory:', Object.keys(postDirectory));
        }
    } catch (error) {
        console.error('[CollectionPage] Error loading PostDirectory:', error);
    }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* 添加透视容器 */
.collection-page-wrapper {
    perspective: 2000px;
    perspective-origin: center center;
}

/* === 优雅的返回按钮 === */
.elegant-back-button {
    position: fixed;
    top: 7rem;
    left: 2rem;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: var(--theme-panel-bg);
    border: 1px solid var(--theme-border-light);
    border-radius: 100px;
    color: var(--theme-body-text);
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.elegant-back-button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--theme-gradient);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.elegant-back-button:hover::before {
    opacity: 0.1;
}

.elegant-back-button svg,
.elegant-back-button .back-text {
    position: relative;
    z-index: 1;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-back-button:hover {
    transform: translateX(-4px);
    box-shadow: 0 8px 24px var(--theme-shadow-lg);
    border-color: var(--theme-primary);
}

.elegant-back-button:hover svg {
    transform: translateX(-4px);
}

.elegant-back-button:active {
    transform: translateX(-2px) scale(0.98);
}

.back-text {
    letter-spacing: 0.02em;
}

/* 响应式：移动端简化按钮 */
@media (max-width: 768px) {
    .elegant-back-button {
        top: 6rem;
        left: 1rem;
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
    }

    .back-text {
        display: none;
    }

    .elegant-back-button {
        width: 44px;
        height: 44px;
        padding: 0;
        justify-content: center;
        border-radius: 50%;
    }
}

.collection-archive {
    min-height: 100vh;
    width: 100%;
    max-width: 100%;
    background: var(--theme-body-bg);
    color: var(--theme-body-text);
    transition: var(--theme-transition-colors);
    opacity: 0;
    transform: rotateY(-90deg) scale(0.8);
    transform-origin: center center;
    animation: pageFlipIn 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.collection-archive.page-ready {
    opacity: 1;
    transform: rotateY(0deg) scale(1);
}

@keyframes pageFlipIn {
    0% {
        opacity: 0;
        transform: rotateY(-90deg) scale(0.8);
    }

    50% {
        opacity: 0.5;
        transform: rotateY(-45deg) scale(0.9);
    }

    100% {
        opacity: 1;
        transform: rotateY(0deg) scale(1);
    }
}

/* === 沉浸式封面区域 === */
.hero-section {
    position: relative;
    height: 60vh;
    min-height: 400px;
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg,
            var(--dominant-color, rgba(0, 0, 0, 0.3)) 0%,
            var(--theme-body-bg) 100%);
    backdrop-filter: blur(2px);
}

.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 2rem;
    max-width: 800px;
}

.collection-meta {
    animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.collection-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 900;
    margin: 0 0 1.5rem 0;
    line-height: 1.1;
    background: var(--theme-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 4px 20px var(--theme-shadow-lg);
}

.collection-stats {
    display: flex;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--theme-body-text);
    background: var(--theme-panel-bg);
    padding: 0.75rem 1.5rem;
    border-radius: 100px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--theme-border-light);
    box-shadow: 0 2px 8px var(--theme-shadow-sm);
}

.stat-item svg {
    opacity: 0.7;
}

/* 滚动指示器 */
.scroll-indicator {
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    color: var(--theme-body-text);
    opacity: 0.6;
    animation: bounce 2s infinite;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateX(-50%) translateY(0);
    }

    50% {
        transform: translateX(-50%) translateY(10px);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* === 时间轴容器 === */
.timeline-container {
    position: relative;
    max-width: 900px;
    margin: 0 auto;
    padding: 4rem 2rem;
}

.timeline-line {
    position: absolute;
    left: 2rem;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg,
            transparent 0%,
            var(--theme-border-medium) 10%,
            var(--theme-border-medium) 90%,
            transparent 100%);
}

/* === 文章卡片 === */
.article-card {
    position: relative;
    margin-left: 4rem;
    margin-bottom: 3rem;
    background: var(--theme-panel-bg);
    border: 1px solid var(--theme-border-light);
    border-radius: 16px;
    padding: 2rem;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px var(--theme-shadow-sm);
}

.article-card:hover {
    transform: translateX(8px) translateY(-4px);
    box-shadow: 0 12px 32px var(--theme-shadow-md);
    border-color: var(--theme-primary);
}

.article-card:hover .timeline-dot {
    transform: scale(1.5);
    background: var(--theme-primary);
    box-shadow: 0 0 0 8px var(--theme-primary-hover);
}

.timeline-dot {
    position: absolute;
    left: -4.5rem;
    top: 2.5rem;
    width: 16px;
    height: 16px;
    background: var(--theme-panel-bg);
    border: 3px solid var(--theme-primary);
    border-radius: 50%;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 0 4px var(--theme-body-bg);
}

.card-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
}

.article-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.3;
    color: var(--theme-heading-text);
    transition: color 0.3s ease;
}

.article-card:hover .article-title {
    color: var(--theme-primary);
}

.article-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--theme-meta-text);
    white-space: nowrap;
    opacity: 0.8;
}

.article-preview {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    color: var(--theme-body-text);
    opacity: 0.85;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.article-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-top: 0.5rem;
}

.tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.tag {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.25rem 0.75rem;
    background: var(--theme-primary);
    color: var(--theme-button-text);
    border-radius: 100px;
    opacity: 0.8;
    transition: opacity 0.3s ease;
}

.article-card:hover .tag {
    opacity: 1;
}

.read-more {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--theme-primary);
    transition: gap 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.article-card:hover .read-more {
    gap: 0.75rem;
}

.read-more svg {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.article-card:hover .read-more svg {
    transform: translateX(4px);
}

/* === 列表过渡动画 === */
.article-list-enter-active {
    transition: all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    transition-delay: calc(var(--index) * 0.1s);
}

.article-list-enter-from {
    opacity: 0;
    transform: translateX(-30px) translateY(20px);
}

/* === 响应式设计 === */
@media (max-width: 768px) {
    .hero-section {
        height: 50vh;
        min-height: 300px;
        background-attachment: scroll;
    }

    .collection-title {
        font-size: 2rem;
    }

    .collection-stats {
        gap: 1rem;
    }

    .stat-item {
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
    }

    .timeline-container {
        padding: 2rem 1rem;
    }

    .timeline-line {
        left: 1rem;
    }

    .article-card {
        margin-left: 2.5rem;
        padding: 1.5rem;
    }

    .timeline-dot {
        left: -3rem;
        width: 12px;
        height: 12px;
    }

    .article-title {
        font-size: 1.4rem;
    }

    .card-header {
        flex-direction: column;
        gap: 0.5rem;
    }

    .article-meta {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media (max-width: 480px) {
    .collection-title {
        font-size: 1.75rem;
    }

    .article-card {
        margin-left: 2rem;
        padding: 1.25rem;
    }

    .timeline-dot {
        left: -2.5rem;
    }
}
</style>
